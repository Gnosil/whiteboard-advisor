"""测试用 FakeLLM:按预置顺序返回 TurnPlan,记录收到的 prompt。"""

from __future__ import annotations

from typing import Optional

from app.models.schemas import Session, TurnPlan


class FakeLLM:
    def __init__(self, plans: list[TurnPlan]):
        self._plans = list(plans)
        self.calls: list[dict] = []

    async def generate_turn(
        self, session: Session, utterance: str, repair_hint: Optional[str] = None
    ) -> TurnPlan:
        self.calls.append(
            {"utterance": utterance, "repair_hint": repair_hint, "session_id": session.id}
        )
        if not self._plans:
            raise AssertionError("FakeLLM 预置的 TurnPlan 已用尽")
        # repair 时返回同一个(模拟 LLM 重试仍给同样输出),否则弹出下一个
        if repair_hint is not None and self._plans:
            return self._plans[0]
        return self._plans.pop(0)
