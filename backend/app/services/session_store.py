"""Session 存储:内存 + 文件持久化(JSON)。

V0.1 用文件持久化(单机即可),支持跨进程 resume。M_future 可换 PostgreSQL+S3。
每轮对话后 save();start 携带 sessionId 时 load() 续航。
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from app.models.schemas import Language, Session, SessionState
from app.services import zone_engine

logger = logging.getLogger("whiteboard-advisor.store")

_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "sessions"
_DATA_DIR.mkdir(parents=True, exist_ok=True)

_CACHE: dict[str, Session] = {}


def _path(session_id: str) -> Path:
    return _DATA_DIR / f"{session_id}.json"


def save(session: Session) -> None:
    from datetime import datetime, timezone

    session.last_active_at = datetime.now(timezone.utc)
    _CACHE[session.id] = session
    try:
        _path(session.id).write_text(session.model_dump_json(indent=2), encoding="utf-8")
    except OSError:
        logger.exception("session 持久化失败: %s", session.id)


def _load(session_id: str) -> Optional[Session]:
    if session_id in _CACHE:
        return _CACHE[session_id]
    p = _path(session_id)
    if not p.exists():
        return None
    try:
        s = Session.model_validate_json(p.read_text(encoding="utf-8"))
        _CACHE[s.id] = s
        return s
    except Exception:  # noqa: BLE001
        logger.exception("session 读取失败: %s", session_id)
        return None


def create(language: Language = Language.zh, template_id: str = "family-protection") -> Session:
    s = Session(language=language, template_id=template_id, state=SessionState.template_loaded)
    zone_engine.init_zones(s)
    save(s)
    return s


def get(session_id: str) -> Optional[Session]:
    return _load(session_id)


def get_or_create(
    session_id: Optional[str], language: Language = Language.zh, template_id: str = "family-protection"
) -> Session:
    if session_id:
        existing = _load(session_id)
        if existing:
            return existing
    return create(language, template_id)


def set_template(session: Session, template_id: str) -> Session:
    """切换模板:重置 zones 为新模板骨架(已有同名 zone 数据保留)。"""
    session.template_id = template_id
    old = session.zones
    session.zones = {}
    zone_engine.init_zones(session)
    for zid, z in session.zones.items():
        if zid in old and old[zid].data:
            session.zones[zid] = old[zid]
    save(session)
    return session
