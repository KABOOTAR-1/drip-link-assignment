from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from coordinator import Coordinator
from utils import audio_validator

# Initialize router
router = APIRouter(
    tags=["language_detection"],
    responses={404: {"description": "Not found"}},
)

# Initialize coordinator
coordinator = Coordinator()

class AudioRequest(BaseModel):
    audio_path: str
    ground_truth_language: str


@router.post("/detect/language")
async def detect_language(request: AudioRequest):
    """
    Detect spoken language from audio file
    """
    try:
        if not request.audio_path:
            raise HTTPException(status_code=400, detail="Audio path not given")
        local_path = audio_validator.get_local_audio_path(request.audio_path)
        isValid, error = audio_validator.validate_audio_file(local_path)

        if(isValid):
            response = await coordinator.detect_language(local_path, request.ground_truth_language)
            return response
        else:
            return error
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/providers")
async def list_providers():
    """
    List all available language detection providers
    """
    providers = []
    for connector in coordinator.connector:
        providers.append({
            "name": connector.provider_name,
            "status": "available"
        })
    
    return {"providers": providers}


