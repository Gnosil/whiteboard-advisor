"""Dialogue 编排:一轮用户输入 → LLM 决策 → zone 校验/应用 → 产出推送事件。

包含核心的 schema-repair 重试:LLM 输出的 zone_data 校验失败时,带错误反馈回灌
LLM 重新生成,最多 2 次,仍失败则降级为纯解释(不改 zone)。
"""

from __future__ import annotations

import logging

from app.models.schemas import (
    ActionType,
    DialogueEntry,
    IntentType,
    Session,
    SessionState,
    TurnPlan,
)
from app.services import llm, zone_engine
from app.services.zone_engine import ZoneValidationError

logger = logging.getLogger("whiteboard-advisor.dialogue")

MAX_REPAIR = 2


async def _resolve_turn(session: Session, utterance: str) -> tuple[TurnPlan, bool]:
    """返回 (plan, applied)。applied 表示 zone_data 是否成功应用。"""
    repair_hint = None
    for attempt in range(MAX_REPAIR + 1):
        plan = await llm.generate_turn(session, utterance, repair_hint)
        if plan.action not in (ActionType.update_zone, ActionType.modify_zone):
            return plan, False
        if not plan.target_zone or plan.zone_data is None:
            return plan, False
        try:
            zone_engine.apply_patch(
                session,
                plan.target_zone,
                plan.zone_data,
                modify=plan.action == ActionType.modify_zone,
            )
            return plan, True
        except ZoneValidationError as e:
            repair_hint = str(e)
            logger.warning("zone_data 校验失败(第%d次): %s", attempt + 1, repair_hint)
    # 2 次修复仍失败:降级为纯解释,不破坏白板
    logger.error("zone_data 修复失败,降级为 explain")
    plan.action = ActionType.explain
    plan.zone_data = None
    return plan, False


async def handle_utterance(session: Session, utterance: str) -> list[dict]:
    """处理一句用户输入,返回要推给客户端的事件列表。"""
    session.dialogue_history.append(DialogueEntry(role="user", content=utterance))
    session.state = SessionState.in_dialogue

    plan, applied = await _resolve_turn(session, utterance)
    events: list[dict] = []

    if applied and plan.target_zone:
        zone = session.zones[plan.target_zone]
        session.current_zone_focus = plan.target_zone
        stale_zones = [
            zid for zid in zone_engine.downstream_of(session, plan.target_zone)
            if session.zones.get(zid) and session.zones[zid].stale
        ]
        events.append(
            {
                "type": "zone_update",
                "zoneId": plan.target_zone,
                "data": zone.data,
                "version": zone.version,
                "animation": "morph" if plan.action == ActionType.modify_zone else "grow",
                "staleZones": stale_zones,
            }
        )

    if plan.intent == IntentType.terminate or plan.action == ActionType.finalize:
        session.state = SessionState.review
        events.append({"type": "finalize", "narration": plan.narration})

    events.append(
        {
            "type": "ai_message",
            "narration": plan.narration,
            "intent": plan.intent.value,
            "targetZone": plan.target_zone,
            "nextQuestion": plan.next_question,
        }
    )

    session.dialogue_history.append(
        DialogueEntry(
            role="ai",
            content=plan.narration,
            intent=plan.intent,
            zone_affected=plan.target_zone,
        )
    )
    return events
