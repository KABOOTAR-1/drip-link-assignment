from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    #cant find free openai_api_key
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    sarvam_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None

    openai_cost_per_1M_input_tokens: float = 1.25
    openai_cost_per_1M_output_tokens: float = 5
    gemini_cost_per_1M_input_tokens: float = 0.70
    gemini_cost_per_1M_output_tokens: float = 0.40
    sarvam_per_hour_rate: float = 30
    elevenlabs_overage_cost_per_hour: float = 0.22
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()