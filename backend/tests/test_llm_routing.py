import pytest

from app.config import settings
from app.models.schemas import ActionType, IntentType, TurnPlan
from app.services import llm
from app.services.llm import TaskKind


@pytest.fixture
def capture_model(monkeypatch):
    captured = {}

    async def fake_call(messages, model):
        captured["model"] = model
        content = TurnPlan(
            intent=IntentType.provide_info,
            action=ActionType.ask_next,
            target_zone=None,
            narration="ok",
        ).model_dump_json()
        return content, {"prompt_tokens": 10, "completion_tokens": 5}

    monkeypatch.setattr(settings, "qianfan_api_key", "test-key")
    monkeypatch.setattr(settings, "qianfan_model", "")
    monkeypatch.setattr(settings, "qianfan_model_fast", "fast-model")
    monkeypatch.setattr(settings, "qianfan_model_deep", "deep-model")
    monkeypatch.setattr(llm, "_call_qianfan", fake_call)
    llm._turn_cache.clear()  # 避免跨用例缓存命中
    return captured


async def test_turn_uses_fast_model(fresh_session, capture_model):
    await llm.generate_turn(fresh_session, "hi", kind=TaskKind.turn)
    assert capture_model["model"] == "fast-model"


async def test_deep_plan_uses_deep_model(fresh_session, capture_model):
    await llm.generate_turn(fresh_session, "hi", kind=TaskKind.deep_plan)
    assert capture_model["model"] == "deep-model"


def test_legacy_qianfan_model_maps_to_deep(monkeypatch):
    monkeypatch.setattr(settings, "qianfan_model", "legacy-deep")
    assert settings.model_deep == "legacy-deep"


async def test_identical_turn_is_cached(fresh_session, capture_model):
    calls = {"n": 0}
    orig = llm._call_qianfan

    async def counting(messages, model):
        calls["n"] += 1
        return await orig(messages, model)

    llm._call_qianfan = counting  # type: ignore
    try:
        await llm.generate_turn(fresh_session, "同一句话")
        await llm.generate_turn(fresh_session, "同一句话")
    finally:
        llm._call_qianfan = orig  # type: ignore
    assert calls["n"] == 1  # 第二次命中缓存
