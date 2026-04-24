"""API test fixtures using the dedicated postgres_test database.

Start the test database before running API tests:
    docker compose up -d postgres_test

Connection defaults match the postgres_test service from docker-compose.yml.
Override via environment variables (TEST_POSTGRES_*) as needed.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.base import Base
from ldk_athlete_ai_coach.db.session import get_db_session
from ldk_athlete_ai_coach.main import app
from tests.factories.database import test_db_url


@pytest.fixture(scope="session")
def pg_engine():
    """Session-scoped engine targeting the postgres_test database.

    Creates the full schema once at the start of the test session and drops
    it when the session ends. No test should ever touch the dev database.
    """
    engine = create_engine(test_db_url())
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(pg_engine) -> Generator[Session, None, None]:
    """Per-test transactional session that rolls back after each test."""
    connection = pg_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient wired to the postgres_test database.

    The ``get_db_session`` dependency is overridden with the per-test
    transactional session so all routes in the test use the same isolated
    session that rolls back after the test completes.
    """

    def _override() -> Session:
        return db_session

    app.dependency_overrides[get_db_session] = _override
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()
