"""family-protection 模板:V0.1 的唯一模板,3 个 zone。

每个 zone 定义:
- id / 双语标题
- JSON Schema(严格约束 LLM 输出的 data 结构)
- order(白板布局顺序)

设计约束(PRD §4.2):LLM 只输出结构化 data,不输出 HTML;校验通过后由前端纯函数渲染。
"""

from __future__ import annotations

TEMPLATE_ID = "family-protection"

ZONE_DEFS: list[dict] = [
    {
        "id": "family_profile",
        "order": 1,
        "title": {"zh": "家庭成员结构", "en": "Family Profile"},
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
                            "role": {"type": "string"},          # 本人 / 配偶 / 子女 / 父母
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
        "id": "protection_gap",
        "order": 2,
        "title": {"zh": "保障缺口分析", "en": "Protection Gap"},
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
                            "category": {"type": "string"},      # 寿险 / 重疾 / 医疗 / 意外
                            "current": {"type": ["number", "null"]},
                            "recommended": {"type": ["number", "null"]},
                            "gap": {"type": ["number", "null"]},
                            "unit": {"type": "string"},          # USD / HKD ...
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
        "order": 3,
        "title": {"zh": "险种配置方案", "en": "Coverage Plan"},
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
                            "type": {"type": "string"},          # 险种
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
]

ZONE_IDS = [z["id"] for z in ZONE_DEFS]
ZONE_BY_ID = {z["id"]: z for z in ZONE_DEFS}


def zone_schema(zone_id: str) -> dict:
    return ZONE_BY_ID[zone_id]["schema"]
