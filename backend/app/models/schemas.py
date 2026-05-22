from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid4())


class Language(str, Enum):
    zh = "zh"
    en = "en"


class IntentType(str, Enum):
    provide_info = "provide_info"
    modify_request = "modify_request"
    clarification_question = "clarification_question"
    topic_switch = "topic_switch"
    out_of_scope = "out_of_scope"
    terminate = "terminate"


class ZoneState(str, Enum):
    empty = "empty"
    partial = "partial"
    filled = "filled"
    modified = "modified"
    locked = "locked"


class SessionState(str, Enum):
    init = "INIT"
    goal_setting = "GOAL_SETTING"
    template_loaded = "TEMPLATE_LOADED"
    in_dialogue = "IN_DIALOGUE"
    review = "REVIEW"
    closed = "CLOSED"


class Zone(BaseModel):
    id: str
    state: ZoneState = ZoneState.empty
    data: dict[str, Any] = Field(default_factory=dict)
    version: int = 0
    stale: bool = False  # 上游 zone 变更后,已填充的下游标记为待更新
    last_updated: datetime = Field(default_factory=_now)


class DialogueEntry(BaseModel):
    timestamp: datetime = Field(default_factory=_now)
    role: str  # "user" | "ai"
    content: str
    intent: Optional[IntentType] = None
    zone_affected: Optional[str] = None


class Session(BaseModel):
    id: str = Field(default_factory=_uuid)
    template_id: str = "family-protection"
    language: Language = Language.zh
    state: SessionState = SessionState.init
    zones: dict[str, Zone] = Field(default_factory=dict)
    dialogue_history: list[DialogueEntry] = Field(default_factory=list)
    current_zone_focus: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)
    last_active_at: datetime = Field(default_factory=_now)


# ---- LLM 编排的结构化输出 ----

class ActionType(str, Enum):
    update_zone = "update_zone"
    modify_zone = "modify_zone"
    explain = "explain"
    switch_focus = "switch_focus"
    ask_next = "ask_next"
    finalize = "finalize"


class TurnPlan(BaseModel):
    """LLM 单轮编排输出。zone_data 必须通过对应 zone 的 JSON Schema 校验。"""

    intent: IntentType
    action: ActionType
    target_zone: Optional[str] = None
    zone_data: Optional[dict[str, Any]] = None
    narration: str = ""
    next_question: Optional[str] = None
