import pytest

from app.models.schemas import ActionType, IntentType, SessionState, TurnPlan
from app.services import dialogue, llm
from tests.fakes import FakeLLM


@pytest.fixture
def patch_llm(monkeypatch):
    def _install(plans):
        fake = FakeLLM(plans)
        monkeypatch.setattr(llm, "generate_turn", fake.generate_turn)
        return fake

    return _install


async def test_provide_info_emits_zone_update_and_message(fresh_session, patch_llm):
    patch_llm(
        [
            TurnPlan(
                intent=IntentType.provide_info,
                action=ActionType.update_zone,
                target_zone="family_profile",
                zone_data={"members": [{"role": "本人", "age": 52}]},
                narration="我在家庭这块画上了你本人。",
            )
        ]
    )
    events = await dialogue.handle_utterance(fresh_session, "我52岁")
    types = [e["type"] for e in events]
    assert "zone_update" in types
    assert "ai_message" in types
    zu = next(e for e in events if e["type"] == "zone_update")
    assert zu["zoneId"] == "family_profile"


async def test_invalid_zone_data_downgrades_to_explain(fresh_session, patch_llm):
    fake = patch_llm(
        [
            TurnPlan(
                intent=IntentType.provide_info,
                action=ActionType.update_zone,
                target_zone="family_profile",
                zone_data={"summary": "缺 members,非法"},
                narration="试图填充。",
            )
        ]
    )
    events = await dialogue.handle_utterance(fresh_session, "随便")
    types = [e["type"] for e in events]
    assert "zone_update" not in types  # 校验失败,未应用
    assert "ai_message" in types
    # 初次 + 2 次修复 = 3 次调用
    assert len(fake.calls) == 3
    assert fake.calls[1]["repair_hint"] is not None


async def test_terminate_emits_finalize(fresh_session, patch_llm):
    patch_llm(
        [
            TurnPlan(
                intent=IntentType.terminate,
                action=ActionType.finalize,
                target_zone=None,
                narration="今天就到这。",
            )
        ]
    )
    events = await dialogue.handle_utterance(fresh_session, "结束")
    assert any(e["type"] == "finalize" for e in events)
    assert fresh_session.state == SessionState.review
