"""规划模板注册表:每个模板 = zones_library 中若干 zone 的组合。"""

from __future__ import annotations

from app.templates import zones_library as zl

TEMPLATES: dict[str, dict] = {
    "family-protection": {
        "title": {"zh": "家庭保障规划", "en": "Family Protection"},
        "zone_ids": ["family_profile", "protection_gap", "coverage_plan"],
    },
    "retirement": {
        "title": {"zh": "退休规划", "en": "Retirement"},
        "zone_ids": ["family_profile", "income_assets", "retirement_cashflow", "summary_dashboard"],
    },
    "education": {
        "title": {"zh": "子女教育金", "en": "Education Fund"},
        "zone_ids": ["family_profile", "education_fund", "coverage_plan", "summary_dashboard"],
    },
    "comprehensive": {
        "title": {"zh": "综合财富配置", "en": "Comprehensive"},
        "zone_ids": [z["id"] for z in zl.ZONE_DEFS if not z["id"].startswith("life_stage")],
    },
    "life-stage": {
        "title": {"zh": "人生阶段规划", "en": "Life-Stage Planning"},
        "zone_ids": ["family_profile", "life_stage_early", "life_stage_mid", "life_stage_retire"],
    },
}

DEFAULT_TEMPLATE = "family-protection"


def exists(template_id: str) -> bool:
    return template_id in TEMPLATES


def template_zone_ids(template_id: str) -> list[str]:
    tid = template_id if template_id in TEMPLATES else DEFAULT_TEMPLATE
    return list(TEMPLATES[tid]["zone_ids"])


def template_zone_defs(template_id: str) -> list[dict]:
    """按 zones_library 的全局 order 排序返回该模板的 zone def。"""
    ids = set(template_zone_ids(template_id))
    return sorted([z for z in zl.ZONE_DEFS if z["id"] in ids], key=lambda z: z["order"])


def template_meta() -> list[dict]:
    return [{"id": tid, "title": t["title"]} for tid, t in TEMPLATES.items()]
