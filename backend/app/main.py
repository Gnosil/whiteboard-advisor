import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.session_ws import router as session_router
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whiteboard-advisor")

app = FastAPI(title="WhiteboardAdvisor API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session_router)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "llm": settings.has_llm,
        "speech": settings.has_speech,
    }
