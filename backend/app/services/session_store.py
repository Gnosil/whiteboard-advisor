"""M2 阶段的内存 session 存储。M4 会替换为持久化实现。"""

from __future__ import annotations

from typing import Optional

from app.models.schemas import Language, Session, SessionState
from app.services import zone_engine

_SESSIONS: dict[str, Session] = {}


def create(language: Language = Language.zh) -> Session:
    s = Session(language=language, state=SessionState.template_loaded)
    zone_engine.init_zones(s)
    _SESSIONS[s.id] = s
    return s


def get(session_id: str) -> Optional[Session]:
    return _SESSIONS.get(session_id)


def get_or_create(session_id: Optional[str], language: Language = Language.zh) -> Session:
    if session_id and session_id in _SESSIONS:
        return _SESSIONS[session_id]
    return create(language)
