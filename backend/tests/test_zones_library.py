"""每个 zone 用一份合法样例 data 应通过校验,一份缺 required 的应失败。"""

from app.services import zone_engine
from app.templates import zones_library as zl

VALID_SAMPLES = {
    "family_profile": {"members": [{"role": "本人", "age": 52}]},
    "income_assets": {"accounts": [{"type": "现金", "value": 100000, "unit": "USD"}]},
    "protection_gap": {"items": [{"category": "寿险", "gap": 3000000, "unit": "USD"}]},
    "coverage_plan": {"products": [{"type": "定期寿险", "rationale": "收入替代"}]},
    "education_fund": {"children": [{"name": "老大", "annual_cost": 50000}]},
    "retirement_cashflow": {"annual_expense": 120000, "unit": "USD"},
    "estate_succession": {"structures": [{"type": "信托"}]},
    "cross_border_notes": {"notes": [{"jurisdiction": "US", "topic": "遗产税"}]},
    "summary_dashboard": {"highlights": [{"label": "总缺口", "value": "400万"}]},
}


def test_all_nine_zones_defined():
    assert len(zl.ZONE_DEFS) == 9
    assert set(VALID_SAMPLES) == set(zl.ALL_ZONE_BY_ID)


def test_valid_samples_pass():
    for zid, data in VALID_SAMPLES.items():
        assert zone_engine.validate_zone_data(zid, data) is None, zid


def test_missing_required_fails():
    for zid in VALID_SAMPLES:
        err = zone_engine.validate_zone_data(zid, {})
        assert err, f"{zid} 空对象应当校验失败"


def test_additional_properties_rejected():
    err = zone_engine.validate_zone_data("family_profile", {"members": [], "bogus": 1})
    assert err
