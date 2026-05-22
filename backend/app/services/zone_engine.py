"""Zone Engine:校验 LLM 输出的 zone_data,应用 patch 到 session。

核心约束(PRD §4.2 验收标准):LLM 输出的 data 必须通过 JSON Schema 校验,
失败则交回 LLM 修复(最多 2 次,由 dialogue 编排)。data 只存结构化数据,渲染交给前端纯函数。
"""

from __future__ import annotations

from typing import Optional

from jsonschema import Draft7Validator

from app.models.schemas import Session, Zone, ZoneState
from app.templates import family_protection as tpl


class ZoneValidationError(Exception):
    pass


def init_zones(session: Session) -> None:
    """加载模板骨架:为每个 zone 建空 state。"""
    for zid in tpl.ZONE_IDS:
        session.zones.setdefault(zid, Zone(id=zid))


def validate_zone_data(zone_id: str, data: dict) -> Optional[str]:
    """返回 None 表示通过,否则返回错误描述(给 LLM 修复用)。"""
    if zone_id not in tpl.ZONE_BY_ID:
        return f"未知 zone: {zone_id}"
    schema = tpl.zone_schema(zone_id)
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if not errors:
        return None
    return "; ".join(f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in errors[:5])


def apply_patch(session: Session, zone_id: str, data: dict, modify: bool = False) -> Zone:
    err = validate_zone_data(zone_id, data)
    if err:
        raise ZoneValidationError(err)
    zone = session.zones.setdefault(zone_id, Zone(id=zone_id))
    zone.data = data
    zone.version += 1
    zone.state = ZoneState.modified if modify else ZoneState.filled
    from datetime import datetime, timezone

    zone.last_updated = datetime.now(timezone.utc)
    return zone


def zone_meta() -> list[dict]:
    """前端用于布局/标题的 zone 元信息。"""
    return [
        {"id": z["id"], "order": z["order"], "title": z["title"]}
        for z in tpl.ZONE_DEFS
    ]
