"""测试用 FakeLLM:按预置顺序返回 TurnPlan,记录收到的 prompt。"""

from __future__ import annotations

from typing import Optional

from app.models.schemas import Session, TurnPlan


class FakeLLM:
    def __init__(self, plans: list[TurnPlan]):
        self._plans = list(plans)
        self._last: Optional[TurnPlan] = None
        self.calls: list[dict] = []

    async def generate_turn(
        self, session: Session, utterance: str, repair_hint: Optional[str] = None
    ) -> TurnPlan:
        self.calls.append(
            {"utterance": utterance, "repair_hint": repair_hint, "session_id": session.id}
        )
        # repair 时重复上一次的输出(模拟 LLM 重试仍给同样的、可能仍非法的结果)
        if repair_hint is not None and self._last is not None:
            return self._last
        if not self._plans:
            raise AssertionError("FakeLLM 预置的 TurnPlan 已用尽")
        self._last = self._plans.pop(0)
        return self._last

    async def generate_turn_stream(self, session: Session, utterance: str, kind=None):
        self.calls.append({"utterance": utterance, "stream": True, "session_id": session.id})
        if not self._plans:
            raise AssertionError("FakeLLM 预置的 TurnPlan 已用尽")
        plan = self._plans.pop(0)
        self._last = plan
        n = plan.narration
        mid = max(1, len(n) // 2)
        yield ("narration", n[:mid])
        yield ("narration", n[mid:])
        yield ("plan", plan)
