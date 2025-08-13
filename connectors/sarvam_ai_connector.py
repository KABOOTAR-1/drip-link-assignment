from .base import BaseConnector
import asyncio
from sarvamai import SarvamAI,AsyncSarvamAI
from config import settings
import math
import os

class Sarvam_AI_Connector(BaseConnector):
    def __init__(self):
        super().__init__("Sarvam_AI")
        self.client = AsyncSarvamAI(api_subscription_key=settings.sarvam_api_key)
        self.rate_per_hour = settings.sarvam_per_hour_rate  # ₹30 per hour
        self.rate_per_second = self.rate_per_hour / 3600

    async def detect_language_implementation(self, audio_path: str) -> tuple[str, float, float]:
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            job = await self.client.speech_to_text_job.create_job(
                                language_code="unknown",
                                model="saarika:v2.5",
                                with_timestamps=True,
                                with_diarization=False
                            )

            await job.upload_files(file_paths=[audio_path])

            await job.start()

            final_status = await job.wait_until_complete()

            if await job.is_failed():
                raise Exception(f"Sarvam AI Batch job failed for file: {audio_path}")

            output_dir = "./sarvam_batch_results"
            os.makedirs(output_dir, exist_ok=True)
            await job.download_outputs(output_dir=output_dir)
            
            result_file = next((f for f in os.listdir(output_dir) if f.endswith(".json")), None)
            if not result_file:
                raise Exception("No transcription result found in output directory.")

            import json
            with open(os.path.join(output_dir, result_file), "r", encoding="utf-8") as f:
                result_data = json.load(f)

            language_code = result_data.get("language_code", None)
            if language_code and len(language_code) > 2:
                language_code = language_code[:2]

            timestamps = result_data.get("timestamps", {})
            if timestamps and "start_time_seconds" in timestamps and "end_time_seconds" in timestamps:
                start_times = timestamps.get("start_time_seconds", [0])
                end_times = timestamps.get("end_time_seconds", [0])
                duration_seconds = math.ceil(max(end_times) - min(start_times))
            else:
                duration_seconds = 0

            total_cost = self.get_estimated_cost(duration_seconds)

            return language_code, duration_seconds, total_cost

        except Exception as e:
            raise Exception(f"Sarvam AI Batch API error: {str(e)}")

    def get_estimated_cost(self, duration_seconds: float) -> float:
        cost = duration_seconds * self.rate_per_second
        print(f"Audio duration: {duration_seconds}s — Estimated cost: ₹{cost:.4f}")
        return cost
