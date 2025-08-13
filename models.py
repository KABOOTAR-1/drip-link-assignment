from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class DetectionStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure" 
    ERROR = "error"

class ProviderResult(BaseModel):
    provider_name: str
    detected_language: Optional[str] = None
    time_taken_seconds: float
    estimated_tokens_or_duration: Optional[float] = None
    estimated_cost_usd: float
    status: DetectionStatus
    error_message: Optional[str] = None

class DetectionRequest(BaseModel):
    audio_file_path: str
    ground_truth_language: Optional[str] = None

class DetectionResponse(BaseModel):
    results: List[ProviderResult]
    total_time_seconds: float
    successful_detections: int