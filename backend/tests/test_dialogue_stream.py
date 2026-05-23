import pytest

from app.models.schemas import ActionType, IntentType, TurnPlan
from app.services import dialogue, llm
from tests.fakes import FakeLLM


@pytest.fixture
def patch_stream(monkeypatch):
    def _install(plans):
        fake = FakeLLM(plans)
        monkeypatch.setattr(llm, "generate_turn_stream", fake.generate_turn_stream)
        monkeypatch.setattr(llm, "generate_turn", fake.generate_turn)
        return fake

    return _install


async def _collect(session, utterance):
    return [ev async for ev in dialogue.handle_utterance_stream(session, utterance)]


async def test_stream_emits_narration_then_zone_update(fresh_session, patch_stream):
    patch_stream(
        [
            TurnPlan(
                intent=IntentType.provide_info,
                action=ActionType.update_zone,
                target_zone="family_profile",
                zone_data={"members": [{"role": "本人", "age": 52}]},
                narration="我在家庭这块画上了你本人的信息。",
            )
        ]
    )
    events = await _collect(fresh_session, "我52岁")
    types = [e["type"] for e in events]
    # 先有 narration_delta,再有 zone_update 与 ai_message
    assert types[0] == "narration_delta"
    assert "zone_update" in types
    assert "ai_message" in types
    # 拼接的 narration_delta == 最终 ai_message narration
    streamed = "".join(e["text"] for e in events if e["type"] == "narration_delta")
    final = next(e for e in events if e["type"] == "ai_message")["narration"]
    assert streamed == final


async def test_stream_out_of_scope_no_zone(fresh_session, patch_stream):
    patch_stream(
        [
            TurnPlan(
                intent=IntentType.out_of_scope,
                action=ActionType.explain,
                target_zone=None,
                narration="这超出我的范围啦。",
            )
        ]
    )
    events = await _collect(fresh_session, "今天几号")
    types = [e["type"] for e in events]
    assert "narration_delta" in types
    assert "free_chat" in types
    assert "zone_update" not in types
