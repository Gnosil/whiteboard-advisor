from app.services import pdf_export, zone_engine


def test_pdf_starts_with_magic(fresh_session):
    zone_engine.apply_patch(fresh_session, "family_profile", {"members": [{"role": "本人", "age": 52}]})
    zone_engine.apply_patch(
        fresh_session, "protection_gap", {"items": [{"category": "寿险", "gap": 3000000, "unit": "USD"}]}
    )
    pdf = pdf_export.render_session_pdf(fresh_session)
    assert pdf[:4] == b"%PDF"
    assert len(pdf) > 1000
