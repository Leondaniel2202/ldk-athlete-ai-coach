"""Integration test fixtures.

Provides shared SQLite database fixtures for integration tests.
The target direction is a dedicated Postgres test database (postgres_test
from docker-compose.yml). SQLite is retained here for CI portability while
the Postgres test service is not yet wired into the CI pipeline.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ldk_athlete_ai_coach.db.base import Base


@pytest.fixture(scope="session")
def sqlite_engine():
    """Create a shared in-memory SQLite engine for the integration test session.

    Foreign-key enforcement is enabled so that referential integrity is
    tested even with SQLite.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    event.listen(
        engine,
        "connect",
        lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"),
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(sqlite_engine) -> Generator[Session, None, None]:
    """Yield a per-test SQLAlchemy session backed by the shared SQLite engine.

    Each test gets a fresh session. Uncommitted changes are rolled back
    after the test completes, keeping tests isolated.
    """
    SessionLocal = sessionmaker(bind=sqlite_engine, class_=Session)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
