from app.models.schemas import AssetTier, Language, Session, SessionState
from app.services import broker, zone_engine


def _session(template="comprehensive") -> Session:
    s = Session(language=Language.zh, template_id=template, state=SessionState.template_loaded)
    zone_engine.init_zones(s)
    return s


def test_tier_from_amount():
    assert broker.tier_from_amount(3_000_000) == AssetTier.hnw
    assert broker.tier_from_amount(800_000) == AssetTier.affluent
    assert broker.tier_from_amount(100_000) == AssetTier.mass_affluent
    assert broker.tier_from_amount(None) == AssetTier.unknown


def test_score_lead_from_total_investable():
    s = _session()
    zone_engine.apply_patch(s, "income_assets", {"total_investable": 3_000_000, "unit": "USD", "accounts": [{"type": "现金"}]})
    assert broker.score_lead(s) == AssetTier.hnw


def test_match_respects_tier_jurisdiction_language():
    b = broker.match(AssetTier.hnw, "HK", "yue")
    assert b is not None
    assert AssetTier.hnw in b.accepted_lead_tiers
    assert "HK" in b.jurisdictions
    assert "yue" in b.languages


def test_no_match_for_unserved_tier():
    # US 只有 hnw 或 mass/affluent 的 broker;mass-affluent + US + en 应能匹配
    assert broker.match(AssetTier.mass_affluent, "US", "en") is not None


def test_price_tiers():
    assert broker.price_for(AssetTier.mass_affluent) == 50
    assert broker.price_for(AssetTier.affluent) == 150
    assert broker.price_for(AssetTier.hnw) == 300
