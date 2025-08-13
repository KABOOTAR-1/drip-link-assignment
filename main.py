from fastapi import FastAPI, HTTPException
import uvicorn
from coordinator import Coordinator
from utils import audio_validator
from pydantic import BaseModel

app=FastAPI(
    title="Multi provier language detection",
    description="detects spoken language",
)

coordinator=Coordinator()

class AudioRequest(BaseModel):
    audio_path: str
    ground_truth_language:str


@app.post("/detect/language")
async def detect_language(request:AudioRequest):
    try:
        if not request.audio_path:
            raise HTTPException(status_code=400, detail="Audio path not given")
        local_path = audio_validator.get_local_audio_path(request.audio_path)
        isValid,error=audio_validator.validate_audio_file(local_path)

        if(isValid):
           response = await coordinator.detect_language(local_path,request.ground_truth_language)
           return response
        else:
            return error
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
@app.get("/providers")
async def list_providers():
    providers = []
    for connector in coordinator.connector:
        providers.append({
            "name": connector.provider_name,
            "status": "available"
        })
    
    return {"providers": providers}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "providers_available": len(coordinator.connector)}


if __name__ == "__main__":
    uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )