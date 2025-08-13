from .base import BaseConnector
from config import settings
from openai import OpenAI
from faster_whisper import WhisperModel
import asyncio

class OpenAI_Connector(BaseConnector):
    def __init__(self):
        super().__init__("OpenAI")
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not provided")
        
        # Your OpenAI client doesnt work cause API is not free
        self.client = OpenAI(api_key=settings.openai_api_key)
        
        self.input_rate = settings.openai_cost_per_1M_input_tokens
        self.output_rate = settings.openai_cost_per_1M_output_tokens
        self.whisper_model = WhisperModel(
            "base", device="cpu", compute_type="int8"
        )

    async def detect_language_implementation(self, audio_path:str) -> tuple[str, float, float]:
        try:
            segments, info = await asyncio.to_thread(
                self.whisper_model.transcribe,
                audio_path,
                beam_size=1,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500),
            )

            # Cant access free api 
            # with open(audio_path, "rb") as audio_file:
            #     print("We have audio_file ",audio_file.fileno)
            #     response = await asyncio.to_thread(
            #         self.client.audio.transcriptions.create,
            #         model="gpt-4o-mini-transcribe", 
            #         file=audio_file,
            #         response_format="json"
            #     )

            detected_language = info.language
            total_tokens = 0  # Not provided by faster_whisper
            total_cost = 0.0  # No cost for local model usage

            full_text = "".join(segment.text for segment in segments)

            return detected_language, total_tokens, total_cost

        except Exception as ex:
            raise Exception(f"Error in local Whisper transcription: {str(ex)}")

    def get_estimated_cost(self, tokens: dict):
        input_tokens = tokens.get('input_tokens', 0)
        output_tokens = tokens.get('output_tokens', 0)
        
        input_cost = (input_tokens / 1_000_000) * self.input_rate
        output_cost = (output_tokens / 1_000_000) * self.output_rate
        total_cost = input_cost + output_cost
        
        return total_cost
