import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Import all ORM models so they are registered on Base.metadata before create_all
import app.persistence.models.phase  # noqa: F401
import app.persistence.models.training_session  # noqa: F401
import app.persistence.models.weekly_feedback  # noqa: F401
import app.persistence.models.workout  # noqa: F401
from app.persistence.models.base import Base


@pytest.fixture
def db_session() -> Session:  # type: ignore[return]
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session  # type: ignore[misc]
    Base.metadata.drop_all(engine)
