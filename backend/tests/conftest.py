import pytest

from app.models.schemas import Language, Session, SessionState
from app.services import zone_engine


@pytest.fixture
def fresh_session() -> Session:
    s = Session(language=Language.zh, state=SessionState.template_loaded)
    zone_engine.init_zones(s)
    return s
