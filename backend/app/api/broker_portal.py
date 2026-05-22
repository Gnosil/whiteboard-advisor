"""Broker portal REST:经纪人查看脱敏 lead 列表、claim(48h SLA)。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services import broker, lead_store

router = APIRouter(prefix="/api/broker")


def _broker_name(broker_id: str | None) -> str | None:
    if not broker_id:
        return None
    for b in broker.brokers():
        if b.id == broker_id:
            return b.name
    return None


@router.get("/leads")
async def list_leads() -> dict:
    leads = lead_store.list_leads()
    return {
        "leads": [
            {
                "id": l.id,
                "tier": l.tier.value,
                "status": l.status.value,
                "matchedBroker": _broker_name(l.matched_broker_id),
                "priceCharged": l.price_charged,
                "risky": l.risky,
                "createdAt": l.created_at.isoformat(),
                "slaDueAt": l.sla_due_at.isoformat() if l.sla_due_at else None,
                # 脱敏:只给名 + 偏好,不给完整联系方式
                "contactName": l.contact.name,
                "preference": l.contact.preference,
                "zoneData": lead_store.session_zone_data(l.session_id),
            }
            for l in leads
        ]
    }


@router.post("/leads/{lead_id}/claim")
async def claim_lead(lead_id: str) -> dict:
    lead = lead_store.claim(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="lead not found")
    return {
        "id": lead.id,
        "status": lead.status.value,
        "slaDueAt": lead.sla_due_at.isoformat() if lead.sla_due_at else None,
    }
