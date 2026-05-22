import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "llm": settings.has_llm,
        "speech": settings.has_speech,
    }


@app.websocket("/ws/session")
async def session_ws(ws: WebSocket) -> None:
    """会话主通道。M1 阶段先做 echo,后续 milestone 接入对话/zone/语音流。"""
    await ws.accept()
    await ws.send_json({"type": "connected", "message": "WhiteboardAdvisor session opened"})
    try:
        while True:
            data = await ws.receive_json()
            logger.info("recv: %s", data)
            await ws.send_json({"type": "echo", "payload": data})
    except WebSocketDisconnect:
        logger.info("client disconnected")
