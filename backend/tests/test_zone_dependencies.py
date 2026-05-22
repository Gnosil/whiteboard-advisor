from app.models.schemas import Language, Session, SessionState
from app.services import zone_engine


def _comprehensive_session() -> Session:
    s = Session(language=Language.zh, template_id="comprehensive", state=SessionState.template_loaded)
    zone_engine.init_zones(s)
    return s


def test_downstream_lookup():
    s = _comprehensive_session()
    # retirement_cashflow 依赖 income_assets
    assert "retirement_cashflow" in zone_engine.downstream_of(s, "income_assets")


def test_upstream_change_marks_filled_downstream_stale():
    s = _comprehensive_session()
    zone_engine.apply_patch(s, "income_assets", {"accounts": [{"type": "现金", "value": 100}]})
    zone_engine.apply_patch(s, "retirement_cashflow", {"annual_expense": 120000, "unit": "USD"})
    assert s.zones["retirement_cashflow"].stale is False
    # 再次更新上游 income_assets → 下游变 stale
    zone_engine.apply_patch(s, "income_assets", {"accounts": [{"type": "股票", "value": 200}]})
    assert s.zones["retirement_cashflow"].stale is True


def test_refresh_downstream_clears_stale():
    s = _comprehensive_session()
    zone_engine.apply_patch(s, "income_assets", {"accounts": [{"type": "现金", "value": 100}]})
    zone_engine.apply_patch(s, "retirement_cashflow", {"annual_expense": 120000, "unit": "USD"})
    zone_engine.apply_patch(s, "income_assets", {"accounts": [{"type": "股票", "value": 200}]})
    assert s.zones["retirement_cashflow"].stale is True
    # 重新填充下游 → stale 清除
    zone_engine.apply_patch(s, "retirement_cashflow", {"annual_expense": 130000, "unit": "USD"})
    assert s.zones["retirement_cashflow"].stale is False
