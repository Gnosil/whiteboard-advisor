import pytest

from app.models.schemas import ActionType, IntentType, TurnPlan
from app.services import dialogue, llm
from tests.fakes import FakeLLM


async def test_out_of_scope_emits_free_chat_no_zone(fresh_session, monkeypatch):
    fake = FakeLLM(
        [
            TurnPlan(
                intent=IntentType.out_of_scope,
                action=ActionType.explain,
                target_zone=None,
                narration="这个问题超出了我的规划范围,不过简单说……",
            )
        ]
    )
    monkeypatch.setattr(llm, "generate_turn", fake.generate_turn)
    events = await dialogue.handle_utterance(fresh_session, "今天天气怎么样?")
    types = [e["type"] for e in events]
    assert "free_chat" in types
    assert "zone_update" not in types
    assert "ai_message" not in types
