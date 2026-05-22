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
    assert metas == {"family-protection", "retirement", "education", "comprehensive"}
