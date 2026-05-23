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
    "life_stage_early": {"items": [{"category": "保险", "action": "配置定期寿险"}], "focus": "积累"},
    "life_stage_mid": {"items": [{"category": "资产配置", "action": "跨境分散配置"}]},
    "life_stage_retire": {"items": [{"category": "传承", "action": "设立信托"}]},
}


def test_all_zones_have_samples():
    assert set(VALID_SAMPLES) == set(zl.ALL_ZONE_BY_ID)


def test_stage_zone_content_is_flexible():
    # 阶段板块的 category 不写死,任意类别都应通过校验
    for cat in ["保险", "资产配置", "教育金", "退休", "传承", "现金流", "税务"]:
        assert zone_engine.validate_zone_data(
            "life_stage_mid", {"items": [{"category": cat, "action": "x"}]}
        ) is None


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
