"""API test fixtures.

Provides a reusable FastAPI TestClient wired to an in-memory SQLite
database so that API tests remain self-contained and never touch the
development or production database.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ldk_athlete_ai_coach.db.base import Base
from ldk_athlete_ai_coach.db.session import get_db_session
from ldk_athlete_ai_coach.main import app


@pytest.fixture(scope="module")
def sqlite_engine():
    """Module-scoped in-memory SQLite engine for API tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def _create_tables(sqlite_engine):
    """Create all tables before each API test and drop them after."""
    Base.metadata.create_all(bind=sqlite_engine)
    yield
    Base.metadata.drop_all(bind=sqlite_engine)


@pytest.fixture()
def db_session(sqlite_engine) -> Session:
    """Return a fresh SQLite session for each API test."""
    SessionLocal = sessionmaker(bind=sqlite_engine, class_=Session)
    return SessionLocal()


@pytest.fixture()
def api_client(db_session: Session) -> Generator[TestClient, None, None]:
    """Return a TestClient wired to the in-memory test database.

    The ``get_db_session`` dependency is overridden so that all routes
    in the test use the same isolated SQLite session.
    """

    def _override() -> Session:
        return db_session

    app.dependency_overrides[get_db_session] = _override
    tc = TestClient(app)
    yield tc
    app.dependency_overrides.clear()
    db_session.close()
