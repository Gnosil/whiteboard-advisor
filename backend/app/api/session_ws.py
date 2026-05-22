import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.models.schemas import ContactInfo, Language
from app.services import dialogue, lead_store, session_store, speech, zone_engine
from app.templates import registry

logger = logging.getLogger("whiteboard-advisor.ws")
router = APIRouter()


async def _run_turn(ws: WebSocket, session, text: str) -> None:
    """处理一句用户输入:对话编排 → 推送事件 → 对 narration 合成 TTS。"""
    await ws.send_json({"type": "thinking", "hint": "正在分析你的需求并作画…"})
    try:
        events = await dialogue.handle_utterance(session, text)
    except Exception as e:  # noqa: BLE001
        logger.exception("turn failed")
        await ws.send_json({"type": "error", "message": f"处理出错: {e}"})
        return
    for ev in events:
        await ws.send_json(ev)
        narration = ev.get("narration") if isinstance(ev, dict) else None
        if ev.get("type") in ("ai_message", "finalize", "free_chat") and narration:
            audio = await speech.synthesize(
                narration, session.language, speech.voice_for_persona(session.voice_persona)
            )
            if audio:
                await ws.send_json({"type": "tts_audio", "format": "mp3", "audio": audio})
    session_store.save(session)


async def _send_started(ws: WebSocket, session) -> None:
    await ws.send_json(
        {
            "type": "session_started",
            "sessionId": session.id,
            "language": session.language.value,
            "templateId": session.template_id,
            "templates": registry.template_meta(),
            "zones": zone_engine.zone_meta(session),
            "speechEnabled": speech.settings.has_speech,
        }
    )
    # resume:把已填充的 zone 重新推给客户端
    for zid, zone in session.zones.items():
        if zone.data:
            await ws.send_json(
                {
                    "type": "zone_update",
                    "zoneId": zid,
                    "data": zone.data,
                    "version": zone.version,
                    "animation": "flash",
                    "stale": zone.stale,
                }
            )


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
                tid = msg.get("templateId") or registry.DEFAULT_TEMPLATE
                session = session_store.get_or_create(msg.get("sessionId"), lang, tid)
                await _send_started(ws, session)
                continue

            if session is None:
                session = session_store.create()
                await _send_started(ws, session)

            if mtype == "set_language":
                session.language = Language(msg.get("language", "zh"))
                continue

            if mtype == "set_persona":
                session.voice_persona = msg.get("persona", "gentleman")
                continue

            if mtype == "set_template":
                tid = msg.get("templateId") or registry.DEFAULT_TEMPLATE
                if registry.exists(tid):
                    session_store.set_template(session, tid)
                    await ws.send_json(
                        {
                            "type": "template_changed",
                            "templateId": session.template_id,
                            "zones": zone_engine.zone_meta(session),
                        }
                    )
                continue

            if mtype == "user_utterance":
                text = (msg.get("text") or "").strip()
                if text:
                    await _run_turn(ws, session, text)
                continue

            if mtype == "lead_capture":
                c = msg.get("contact") or {}
                contact = ContactInfo(
                    name=c.get("name", ""),
                    phone=c.get("phone", ""),
                    email=c.get("email", ""),
                    preference=c.get("preference", ""),
                )
                lead, matched = lead_store.capture(session, contact)
                if lead.risky:
                    await ws.send_json(
                        {"type": "lead_result", "matched": False, "message": "我们会尽快与你联系。"}
                    )
                elif matched:
                    await ws.send_json(
                        {
                            "type": "lead_result",
                            "matched": True,
                            "broker": {
                                "name": matched.name,
                                "city": matched.city,
                                "years": matched.years_experience,
                            },
                            "message": (
                                f"我们已为你匹配 {matched.name}({matched.city},{matched.years_experience} 年经验)。"
                                f"她将在 48 小时内联系你,届时已看过你今天画的规划草图。"
                            ),
                        }
                    )
                else:
                    await ws.send_json(
                        {"type": "lead_result", "matched": False, "message": "暂未匹配到合适的经纪人,我们会人工跟进。"}
                    )
                continue

            if mtype == "lead_cancel":
                c = msg.get("contact") or {}
                lead_store.record_cancel(
                    ContactInfo(name=c.get("name", ""), phone=c.get("phone", ""), email=c.get("email", ""))
                )
                continue

            if mtype == "audio":
                audio_b64 = msg.get("data")
                if not audio_b64:
                    continue
                transcript = await speech.transcribe(audio_b64, session.language)
                if not transcript:
                    await ws.send_json(
                        {"type": "asr_failed", "message": "没听清,可以再说一次或改用文字。"}
                    )
                    continue
                await ws.send_json({"type": "asr_result", "text": transcript})
                await _run_turn(ws, session, transcript)
                continue
    except WebSocketDisconnect:
        logger.info("client disconnected")
