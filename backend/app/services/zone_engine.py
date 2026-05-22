"""Zone Engine:校验 LLM 输出的 zone_data,应用 patch,管理依赖与下游失效。

核心约束(PRD §4.2):LLM 输出的 data 必须通过 JSON Schema 校验,失败交回 LLM 修复
(最多 2 次,由 dialogue 编排)。data 只存结构化数据,渲染交给前端纯函数。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from jsonschema import Draft7Validator

from app.models.schemas import Session, Zone, ZoneState
from app.templates import registry
from app.templates import zones_library as zl


class ZoneValidationError(Exception):
    pass


def init_zones(session: Session) -> None:
    """按 session 模板加载 zone 骨架。"""
    for zid in registry.template_zone_ids(session.template_id):
        session.zones.setdefault(zid, Zone(id=zid))


def validate_zone_data(zone_id: str, data: dict) -> Optional[str]:
    """返回 None 表示通过,否则返回错误描述(给 LLM 修复用)。"""
    if zone_id not in zl.ALL_ZONE_BY_ID:
        return f"未知 zone: {zone_id}"
    validator = Draft7Validator(zl.zone_schema(zone_id))
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if not errors:
        return None
    return "; ".join(f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in errors[:5])


def downstream_of(session: Session, zone_id: str) -> list[str]:
    """返回当前 session 中、依赖 zone_id 的 zone(仅限本模板含有的)。"""
    in_template = set(registry.template_zone_ids(session.template_id))
    out = []
    for zid in in_template:
        if zone_id in zl.zone_dependencies(zid):
            out.append(zid)
    return out


def apply_patch(session: Session, zone_id: str, data: dict, modify: bool = False) -> Zone:
    err = validate_zone_data(zone_id, data)
    if err:
        raise ZoneValidationError(err)
    zone = session.zones.setdefault(zone_id, Zone(id=zone_id))
    zone.data = data
    zone.version += 1
    zone.state = ZoneState.modified if modify else ZoneState.filled
    zone.stale = False
    zone.last_updated = datetime.now(timezone.utc)
    # 上游变更 → 已填充的下游标记 stale
    for dzid in downstream_of(session, zone_id):
        dz = session.zones.get(dzid)
        if dz and dz.data:
            dz.stale = True
    return zone


def zone_meta(session: Session) -> list[dict]:
    """前端布局/标题用的 zone 元信息(按 session 模板)。"""
    return [
        {"id": z["id"], "order": z["order"], "title": z["title"]}
        for z in registry.template_zone_defs(session.template_id)
    ]
