from datetime import datetime, timedelta, timezone

from app.services import session_store, zone_engine


def test_share_roundtrip():
    s = session_store.create()
    zone_engine.apply_patch(s, "family_profile", {"members": [{"role": "本人"}]})
    session_store.save(s)
    token = session_store.ensure_share(s)
    resolved = session_store.resolve_share(token)
    assert resolved is not None
    assert resolved.id == s.id


def test_expired_share_returns_none():
    s = session_store.create()
    token = session_store.ensure_share(s)
    s.share_expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    session_store.save(s)
    assert session_store.resolve_share(token) is None


def test_unknown_token():
    assert session_store.resolve_share("does-not-exist") is None
