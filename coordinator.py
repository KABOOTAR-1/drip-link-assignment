from typing import List
from config import settings
from models import DetectionResponse, ProviderResult,DetectionStatus
from connectors import OpenAI_Connector ,Gemini_Connector,Sarvam_AI_Connector, ElevenLabs_Connector
import asyncio
from time import time

class Coordinator:
    def __init__(self):
        self.connector=[]
        self._initialize_connectors()
    
    def _initialize_connectors(self):
        """Initialize all available connectors"""
        try:
            if settings.openai_api_key:
                self.connector.append(OpenAI_Connector())
        except Exception as e:
            print(f"Failed to initialize OpenAI connector: {e}")
        
        try:
            if settings.google_api_key:
                self.connector.append(Gemini_Connector())
        except Exception as e:
            print(f"Failed to initialize Google connector: {e}")
        
        try:
            if settings.sarvam_api_key:
                self.connector.append(Sarvam_AI_Connector())
        except Exception as e:
            print(f"Failed to initialize SarvamAI connector: {e}")

        try:
            if settings.elevenlabs_api_key:
                print("Initializing ElevenLabs connector")
                self.connector.append(ElevenLabs_Connector())
        except Exception as e:
            print(f"Failed to initialize ElevenLabs connector: {e}")

    async def detect_language(self,audio_path:list[str],ground_truth_language:str)->DetectionResponse:
        start_time = time()
        tasks = [
            connector.detect_language(audio_path,ground_truth_language) for connector in self.connector
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        provider_results =[]
        successful_count = 0

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                  provider_results.append(ProviderResult(
                    provider_name=f"Provider_{i}",
                    time_taken_seconds=0.0,
                    estimated_tokens=0,
                    estimated_cost_usd=0.0,
                    status=DetectionStatus.ERROR,
                    error_message=str(result)
                ))
            else:
                provider_results.append(result)
                if result.status == DetectionStatus.SUCCESS:
                    successful_count += 1

        total_time = time() - start_time
        return DetectionResponse(
            results=provider_results,
            total_time_seconds=total_time,
            successful_detections=successful_count
        )