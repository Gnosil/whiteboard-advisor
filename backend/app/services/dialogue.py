"""Dialogue 编排:用户输入 → LLM 决策 → zone 校验/应用 → 推送事件。

两个入口:
- handle_utterance:非流式,返回事件列表(测试与回退用)
- handle_utterance_stream:流式,先吐 narration_delta,再吐 zone_update / ai_message

核心 schema-repair:zone_data 校验失败时带错误回灌 LLM(最多 2 次),仍失败则降级为纯解释。
"""

from __future__ import annotations

import logging
from typing import AsyncIterator

from app.models.schemas import (
    ActionType,
    DialogueEntry,
    IntentType,
    Session,
    SessionState,
    TurnPlan,
)
from app.services import cost, guardrails, llm, zone_engine
from app.services.zone_engine import ZoneValidationError

logger = logging.getLogger("whiteboard-advisor.dialogue")

MAX_REPAIR = 2

_BUDGET_MSG = "今天我们已经聊了不少,先到这儿吧。要不要让一位持牌经纪人帮你深入做一版?"


async def _apply_zone_with_repair(session: Session, utterance: str, plan: TurnPlan) -> bool:
    """对 plan 的 zone_data 做校验+应用,失败则回灌 LLM 修复(最多 2 次)。
    返回 applied;彻底失败则把 plan 降级为 explain 并返回 False。"""
    if plan.action not in (ActionType.update_zone, ActionType.modify_zone):
        return False
    if not plan.target_zone or plan.zone_data is None:
        return False

    for attempt in range(MAX_REPAIR + 1):
        try:
            zone_engine.apply_patch(
                session, plan.target_zone, plan.zone_data, modify=plan.action == ActionType.modify_zone
            )
            return True
        except ZoneValidationError as e:
            logger.warning("zone_data 校验失败(第%d次): %s", attempt + 1, e)
            if attempt < MAX_REPAIR:
                repaired = await llm.generate_turn(session, utterance, repair_hint=str(e))
                plan.zone_data = repaired.zone_data
                if repaired.target_zone:
                    plan.target_zone = repaired.target_zone
    logger.error("zone_data 修复失败,降级为 explain")
    plan.action = ActionType.explain
    plan.zone_data = None
    return False


def _budget_events() -> list[dict]:
    return [
        {"type": "finalize", "narration": _BUDGET_MSG},
        {"type": "ai_message", "narration": _BUDGET_MSG, "intent": "terminate", "targetZone": None, "nextQuestion": None},
    ]


def _tail_events(session: Session, plan: TurnPlan, applied: bool) -> list[dict]:
    """guardrails 已由调用方应用。构建 zone_update / finalize / ai_message 并落历史。"""
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
        DialogueEntry(role="ai", content=plan.narration, intent=plan.intent, zone_affected=plan.target_zone)
    )
    return events


def _sanitize(plan: TurnPlan) -> None:
    clean, violations = guardrails.sanitize(plan.narration)
    if violations:
        logger.warning("guardrails 命中: %s", violations)
    plan.narration = clean


def _free_chat(session: Session, plan: TurnPlan) -> dict:
    session.dialogue_history.append(
        DialogueEntry(role="ai", content=plan.narration, intent=plan.intent)
    )
    return {"type": "free_chat", "narration": plan.narration}


async def handle_utterance(session: Session, utterance: str) -> list[dict]:
    """非流式:一次性返回事件列表。"""
    session.dialogue_history.append(DialogueEntry(role="user", content=utterance))
    session.state = SessionState.in_dialogue

    try:
        plan = await llm.generate_turn(session, utterance)
        applied = await _apply_zone_with_repair(session, utterance, plan)
    except cost.BudgetExceeded:
        session.state = SessionState.review
        return _budget_events()

    _sanitize(plan)
    if plan.intent == IntentType.out_of_scope:
        return [_free_chat(session, plan)]
    return _tail_events(session, plan, applied)


async def handle_utterance_stream(session: Session, utterance: str) -> AsyncIterator[dict]:
    """流式:先 yield narration_delta,再 yield zone_update / finalize / ai_message。"""
    session.dialogue_history.append(DialogueEntry(role="user", content=utterance))
    session.state = SessionState.in_dialogue

    plan: TurnPlan | None = None
    try:
        async for typ, payload in llm.generate_turn_stream(session, utterance):
            if typ == "narration":
                if payload:
                    yield {"type": "narration_delta", "text": payload}
            elif typ == "plan":
                plan = payload
    except cost.BudgetExceeded:
        session.state = SessionState.review
        for ev in _budget_events():
            yield ev
        return

    if plan is None:
        return

    applied = await _apply_zone_with_repair(session, utterance, plan)
    _sanitize(plan)
    if plan.intent == IntentType.out_of_scope:
        yield _free_chat(session, plan)
        return
    for ev in _tail_events(session, plan, applied):
        yield ev
