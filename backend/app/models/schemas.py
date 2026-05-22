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
    llm_cost: float = 0.0  # 累计 LLM 估算成本 (USD)
    share_token: Optional[str] = None
    share_expires_at: Optional[datetime] = None
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


class AssetTier(str, Enum):
    mass_affluent = "mass-affluent"  # < $500K
    affluent = "affluent"            # $500K - $2M
    hnw = "hnw"                      # > $2M
    unknown = "unknown"


class LeadStatus(str, Enum):
    pending = "pending"
    matched = "matched"
    contacted = "contacted"
    closed_won = "closed_won"
    closed_lost = "closed_lost"


class ContactInfo(BaseModel):
    name: str = ""
    phone: str = ""
    email: str = ""
    preference: str = ""


class Lead(BaseModel):
    id: str = Field(default_factory=_uuid)
    session_id: str
    status: LeadStatus = LeadStatus.pending
    tier: AssetTier = AssetTier.unknown
    matched_broker_id: Optional[str] = None
    price_charged: Optional[float] = None
    contact: ContactInfo = Field(default_factory=ContactInfo)
    risky: bool = False
    created_at: datetime = Field(default_factory=_now)
    claimed_at: Optional[datetime] = None
    sla_due_at: Optional[datetime] = None


class Broker(BaseModel):
    id: str
    name: str
    city: str = ""
    jurisdictions: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    specialties: list[str] = Field(default_factory=list)
    accepted_lead_tiers: list[AssetTier] = Field(default_factory=list)
    years_experience: int = 0


class KnowledgeChunk(BaseModel):
    id: str
    jurisdiction: str  # US / HK / CA / global
    category: str      # product / tax_rule / regulation / methodology
    text: str
    source: str
    confidence_level: str = "scraped"  # official / derived / scraped
    effective_date: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)


class TurnPlan(BaseModel):
    """LLM 单轮编排输出。zone_data 必须通过对应 zone 的 JSON Schema 校验。"""

    intent: IntentType
    action: ActionType
    target_zone: Optional[str] = None
    zone_data: Optional[dict[str, Any]] = None
    narration: str = ""
    next_question: Optional[str] = None
