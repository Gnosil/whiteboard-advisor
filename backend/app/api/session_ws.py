import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.models.schemas import Language
from app.services import dialogue, session_store, zone_engine

logger = logging.getLogger("whiteboard-advisor.ws")
router = APIRouter()


@router.websocket("/ws/session")
async def session_ws(ws: WebSocket) -> None:
    await ws.accept()
    session = None
    try:
        while True:
            msg = await ws.receive_json()
            mtype = msg.get("type")

            if mtype == "start":
                lang = Language(msg.get("language", "zh"))
                session = session_store.get_or_create(msg.get("sessionId"), lang)
                await ws.send_json(
                    {
                        "type": "session_started",
                        "sessionId": session.id,
                        "language": session.language.value,
                        "zones": zone_engine.zone_meta(),
                    }
                )
                continue

            if session is None:
                session = session_store.create()
                await ws.send_json(
                    {
                        "type": "session_started",
                        "sessionId": session.id,
                        "language": session.language.value,
                        "zones": zone_engine.zone_meta(),
                    }
                )

            if mtype == "user_utterance":
                text = (msg.get("text") or "").strip()
                if not text:
                    continue
                await ws.send_json({"type": "thinking"})
                try:
                    events = await dialogue.handle_utterance(session, text)
                    for ev in events:
                        await ws.send_json(ev)
                except Exception as e:  # noqa: BLE001
                    logger.exception("turn failed")
                    await ws.send_json(
                        {"type": "error", "message": f"处理出错: {e}"}
                    )
    except WebSocketDisconnect:
        logger.info("client disconnected")
