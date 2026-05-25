from app.templates import registry


def test_comprehensive_has_nine_zones():
    assert len(registry.template_zone_ids("comprehensive")) == 9


def test_retirement_zones():
    ids = registry.template_zone_ids("retirement")
    assert "retirement_cashflow" in ids
    assert "coverage_plan" not in ids


def test_unknown_template_falls_back_to_default():
    assert registry.template_zone_ids("nope") == registry.template_zone_ids(registry.DEFAULT_TEMPLATE)


def test_zone_defs_sorted_by_order():
    defs = registry.template_zone_defs("comprehensive")
    orders = [d["order"] for d in defs]
    assert orders == sorted(orders)


def test_template_meta_lists_all():
    metas = {m["id"] for m in registry.template_meta()}
    assert metas == {"family-protection", "retirement", "education", "comprehensive", "life-stage"}


def test_layout_timeline_only_for_life_stage():
    assert registry.template_layout("life-stage") == "timeline"
    assert registry.template_layout("family-protection") == "grid"
    assert registry.template_layout("comprehensive") == "grid"
    assert registry.template_layout("unknown") == "grid"


def test_life_stage_template_zones_ordered():
    ids = registry.template_zone_ids("life-stage")
    assert ids == ["family_profile", "life_stage_early", "life_stage_mid", "life_stage_retire"]
    # 按全局 order 排序后,阶段板块在 family_profile 之后且依次排列
    defs = registry.template_zone_defs("life-stage")
    assert [d["id"] for d in defs] == ids
