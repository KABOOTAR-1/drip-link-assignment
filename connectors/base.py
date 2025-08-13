from models import ProviderResult,DetectionStatus
import time
import os
from abc import ABC,abstractmethod

class BaseConnector(ABC):

    def __init__(self, name: str):
        self.name = name
    
    async def detect_language(self, audio_path: str,ground_truth_language:str) ->ProviderResult :
        start_time = time.time()
        
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            language_code, tokens, cost = await self.detect_language_implementation(audio_path)
            time_taken = time.time() - start_time
            
            if language_code:
                return ProviderResult(
                    provider_name=self.name,
                    detected_language=language_code,
                    time_taken_seconds=round(time_taken, 3),
                    estimated_tokens_or_duration=tokens,
                    estimated_cost_usd=round(cost, 6),
                    status = DetectionStatus.SUCCESS if language_code == ground_truth_language else DetectionStatus.FAILURE
                )
            else:
                return ProviderResult(
                    provider_name=self.name,
                    time_taken_seconds=round(time_taken, 3),
                    estimated_tokens_or_duration=tokens,
                    estimated_cost_usd=round(cost, 6),
                    status=DetectionStatus.FAILURE,
                    error_message="No language detected"
                )
                
        except Exception as e:
            time_taken = time.time() - start_time
            return ProviderResult(
                provider_name=self.name,
                time_taken_seconds=round(time_taken, 3),
                estimated_tokens_or_duration=0,
                estimated_cost_usd=0.0,
                status=DetectionStatus.ERROR,
                error_message=str(e)
            )
    @abstractmethod
    def get_estimated_cost(self, tokens) -> float:
        raise NotImplementedError("Subclasses should implement this method.")
    
    @abstractmethod
    async def detect_language_implementation(self, audio_path: str) -> tuple[str,float,float]:
        raise NotImplementedError("Subclasses should implement this method.")
    