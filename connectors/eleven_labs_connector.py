import asyncio
from .base import BaseConnector
import elevenlabs
from config import settings

class ElevenLabs_Connector(BaseConnector):
    def __init__(self):
        super().__init__("ElevenLabs")
        self.client = elevenlabs.ElevenLabs(api_key=settings.elevenlabs_api_key)
        self.overage_rate = settings.elevenlabs_overage_cost_per_hour

    async def detect_language_implementation(self, audio_path:str):

        try:
            with open(audio_path, "rb") as audio_file:
                response = await asyncio.to_thread(
                    self.client.speech_to_text.convert,
                    model_id="scribe_v1",
                    file=audio_file
                )
            #print(response)
            lang = response.language_code
            language_code = lang[:2] if len(lang) > 2 else lang

            words = response.words or []
            if words:
                total_seconds = max(word.end for word in words)
            else:
                total_seconds = 0.0

            total_cost=self.get_estimated_cost(total_seconds)
            return language_code, float(total_seconds), total_cost

        except Exception as ex:
            raise Exception("Eleven Labs API error: " + str(ex))

    def get_estimated_cost(self, duration_seconds: float) -> float:
        """
        this is after the 6000 hours of the business plan have expired
        """
        hours = duration_seconds / 3600.0
        return hours * self.overage_rate

