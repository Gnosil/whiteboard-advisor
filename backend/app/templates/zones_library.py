"""全部 9 个 zone 的定义库(id / order / 双语标题 / JSON Schema / dependencies)。

各模板从此库挑选 zone 组合(见 registry.py)。
设计约束(PRD §4.2):LLM 只产出结构化 data,schema 严格约束(additionalProperties:false + required)。
"""

from __future__ import annotations


def _stage_schema() -> dict:
    """人生阶段规划板块的灵活 schema:骨架固定,内容(items)灵活,
    category 不写死(保险/资产配置/教育金/退休/传承/现金流/税务…均可)。"""
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["items"],
        "properties": {
            "age_range": {"type": "string"},   # 该阶段对应的实际年龄区间(AI 按客户年龄填)
            "focus": {"type": "string"},        # 这个阶段的规划重点
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["category", "action"],
                    "properties": {
                        "category": {"type": "string"},  # 保险 / 资产配置 / 教育金 / 退休 / 传承 / 现金流 / 税务
                        "action": {"type": "string"},    # 具体规划动作/建议
                        "priority": {"type": ["string", "null"]},  # 高/中/低
                        "note": {"type": "string"},
                    },
                },
            },
            "summary": {"type": "string"},
        },
    }


# 每个 zone:id, order(全局布局序), title{zh,en}, schema, dependencies
ZONE_DEFS: list[dict] = [
    {
        "id": "family_profile",
        "order": 1,
        "title": {"zh": "家庭成员结构", "en": "Family Profile"},
        "dependencies": [],
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["members"],
            "properties": {
                "members": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["role"],
                        "properties": {
                            "role": {"type": "string"},
                            "name": {"type": "string"},
                            "age": {"type": ["integer", "null"]},
                            "location": {"type": "string"},
                            "note": {"type": "string"},
                        },
                    },
                },
                "summary": {"type": "string"},
            },
        },
    },
    {
        "id": "income_assets",
        "order": 2,
        "title": {"zh": "收入资产盘点", "en": "Income & Assets"},
        "dependencies": [],
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["accounts"],
            "properties": {
                "accounts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["type"],
                        "properties": {
                            "type": {"type": "string"},        # 现金 / 股票 / 房产 / 企业 / 退休账户
                            "value": {"type": ["number", "null"]},
                            "unit": {"type": "string"},
                            "note": {"type": "string"},
                        },
                    },
                },
                "total_investable": {"type": ["number", "null"]},
                "unit": {"type": "string"},
                "summary": {"type": "string"},
            },
        },
    },
    {
        "id": "protection_gap",
        "order": 3,
        "title": {"zh": "保障缺口分析", "en": "Protection Gap"},
        "dependencies": ["family_profile", "income_assets"],
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["items"],
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["category", "gap"],
                        "properties": {
                            "category": {"type": "string"},
                            "current": {"type": ["number", "null"]},
                            "recommended": {"type": ["number", "null"]},
                            "gap": {"type": ["number", "null"]},
                            "unit": {"type": "string"},
                            "note": {"type": "string"},
                        },
                    },
                },
                "summary": {"type": "string"},
            },
        },
    },
    {
        "id": "coverage_plan",
        "order": 4,
        "title": {"zh": "险种配置方案", "en": "Coverage Plan"},
        "dependencies": ["protection_gap"],
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["products"],
            "properties": {
                "products": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["type", "rationale"],
                        "properties": {
                            "type": {"type": "string"},
                            "coverage": {"type": ["number", "null"]},
                            "term": {"type": "string"},
                            "est_premium": {"type": ["number", "null"]},
                            "unit": {"type": "string"},
                            "rationale": {"type": "string"},
                        },
                    },
                },
                "total_premium": {"type": ["number", "null"]},
                "disclaimer": {"type": "string"},
            },
        },
    },
    {
        "id": "education_fund",
        "order": 5,
        "title": {"zh": "子女教育金规划", "en": "Education Fund"},
        "dependencies": ["family_profile", "income_assets"],
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["children"],
            "properties": {
                "children": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string"},
                            "location": {"type": "string"},
                            "start_year": {"type": ["integer", "null"]},
                            "annual_cost": {"type": ["number", "null"]},
                            "years": {"type": ["integer", "null"]},
                            "unit": {"type": "string"},
                        },
                    },
                },
                "total_need": {"type": ["number", "null"]},
                "funding_gap": {"type": ["number", "null"]},
                "unit": {"type": "string"},
                "summary": {"type": "string"},
            },
        },
    },
    {
        "id": "retirement_cashflow",
        "order": 6,
        "title": {"zh": "退休现金流推演", "en": "Retirement Cashflow"},
        "dependencies": ["income_assets"],
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["annual_expense"],
            "properties": {
                "retire_age": {"type": ["integer", "null"]},
                "annual_expense": {"type": ["number", "null"]},
                "income_sources": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string"},
                            "annual": {"type": ["number", "null"]},
                            "from_age": {"type": ["integer", "null"]},
                        },
                    },
                },
                "gap_years": {"type": ["integer", "null"]},
                "unit": {"type": "string"},
                "summary": {"type": "string"},
            },
        },
    },
    {
        "id": "estate_succession",
        "order": 7,
        "title": {"zh": "财富传承结构", "en": "Estate & Succession"},
        "dependencies": ["income_assets", "family_profile"],
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["structures"],
            "properties": {
                "structures": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["type"],
                        "properties": {
                            "type": {"type": "string"},        # 遗嘱 / 信托 / 保单架构 / 赠与
                            "beneficiary": {"type": "string"},
                            "jurisdiction": {"type": "string"},
                            "note": {"type": "string"},
                        },
                    },
                },
                "tax_notes": {"type": "string"},
                "summary": {"type": "string"},
            },
        },
    },
    {
        "id": "cross_border_notes",
        "order": 8,
        "title": {"zh": "跨境注意事项", "en": "Cross-Border Notes"},
        "dependencies": [],
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["notes"],
            "properties": {
                "notes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["jurisdiction", "topic"],
                        "properties": {
                            "jurisdiction": {"type": "string"},
                            "topic": {"type": "string"},
                            "detail": {"type": "string"},
                        },
                    },
                },
                "summary": {"type": "string"},
            },
        },
    },
    {
        "id": "summary_dashboard",
        "order": 9,
        "title": {"zh": "总览仪表盘", "en": "Summary Dashboard"},
        "dependencies": [],
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["highlights"],
            "properties": {
                "highlights": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["label", "value"],
                        "properties": {
                            "label": {"type": "string"},
                            "value": {"type": "string"},
                            "unit": {"type": "string"},
                        },
                    },
                },
                "action_items": {"type": "array", "items": {"type": "string"}},
                "summary": {"type": "string"},
            },
        },
    },
    # ---- 人生阶段规划(时间维度,内容灵活)----
    {
        "id": "life_stage_early",
        "order": 10,
        "title": {"zh": "积累期 (≈40岁前)", "en": "Accumulation (≤40)"},
        "dependencies": ["family_profile"],
        "schema": _stage_schema(),
    },
    {
        "id": "life_stage_mid",
        "order": 11,
        "title": {"zh": "成熟期 (40–60岁)", "en": "Maturity (40–60)"},
        "dependencies": ["family_profile"],
        "schema": _stage_schema(),
    },
    {
        "id": "life_stage_retire",
        "order": 12,
        "title": {"zh": "退休期 (60岁后)", "en": "Retirement (60+)"},
        "dependencies": ["family_profile"],
        "schema": _stage_schema(),
    },
]

ALL_ZONE_BY_ID = {z["id"]: z for z in ZONE_DEFS}


def zone_def(zone_id: str) -> dict:
    return ALL_ZONE_BY_ID[zone_id]


def zone_schema(zone_id: str) -> dict:
    return ALL_ZONE_BY_ID[zone_id]["schema"]


def zone_dependencies(zone_id: str) -> list[str]:
    return ALL_ZONE_BY_ID[zone_id].get("dependencies", [])
