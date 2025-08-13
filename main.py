from fastapi import FastAPI
import uvicorn
from routers import language_detection

# Initialize FastAPI application
app = FastAPI(
    title="Multi-provider Language Detection API",
    description="API for detecting spoken language from audio using multiple providers",
    version="1.0.0"
)

# Include routers
app.include_router(language_detection.router)

if __name__ == "__main__":
    uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )