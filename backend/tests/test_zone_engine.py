import pytest

from app.models.schemas import ZoneState
from app.services import zone_engine
from app.services.zone_engine import ZoneValidationError

VALID_FAMILY = {
    "members": [{"role": "本人", "age": 52, "location": "香港"}],
    "summary": "跨境家庭",
}


def test_valid_data_passes():
    assert zone_engine.validate_zone_data("family_profile", VALID_FAMILY) is None


def test_missing_required_fails():
    err = zone_engine.validate_zone_data("family_profile", {"summary": "x"})
    assert err and "members" in err


def test_unknown_zone():
    assert "未知 zone" in zone_engine.validate_zone_data("nope", {})


def test_apply_patch_bumps_version_and_state(fresh_session):
    z = zone_engine.apply_patch(fresh_session, "family_profile", VALID_FAMILY)
    assert z.version == 1
    assert z.state == ZoneState.filled
    z2 = zone_engine.apply_patch(fresh_session, "family_profile", VALID_FAMILY, modify=True)
    assert z2.version == 2
    assert z2.state == ZoneState.modified


def test_apply_patch_invalid_raises(fresh_session):
    with pytest.raises(ZoneValidationError):
        zone_engine.apply_patch(fresh_session, "family_profile", {"summary": "no members"})
