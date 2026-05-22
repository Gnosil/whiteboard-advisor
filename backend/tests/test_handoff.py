from app.models.schemas import ContactInfo, LeadStatus, Language, Session, SessionState
from app.services import broker, lead_store, session_store, zone_engine


def _hk_hnw_session() -> Session:
    s = session_store.create(Language.zh, "comprehensive")
    zone_engine.apply_patch(
        s, "family_profile", {"members": [{"role": "本人", "location": "香港"}], "summary": "香港家庭"}
    )
    zone_engine.apply_patch(
        s, "income_assets", {"total_investable": 3_000_000, "unit": "USD", "accounts": [{"type": "现金"}]}
    )
    session_store.save(s)
    return s


def test_capture_matches_broker():
    s = _hk_hnw_session()
    lead, matched = lead_store.capture(s, ContactInfo(name="Henry", email="henry@example.com"))
    assert matched is not None
    assert lead.status == LeadStatus.matched
    assert lead.price_charged == broker.price_for(lead.tier)


def test_repeated_cancel_marks_risky():
    s = _hk_hnw_session()
    contact = ContactInfo(name="X", email="repeat@example.com")
    lead_store.record_cancel(contact)
    lead_store.record_cancel(contact)
    assert lead_store.is_risky(contact)
    lead, matched = lead_store.capture(s, contact)
    assert lead.risky is True
    assert matched is None


def test_claim_sets_sla():
    s = _hk_hnw_session()
    lead, _ = lead_store.capture(s, ContactInfo(name="Henry", email="claim@example.com"))
    claimed = lead_store.claim(lead.id)
    assert claimed.status == LeadStatus.contacted
    assert claimed.sla_due_at is not None
