"""API test fixtures."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.session import get_db_session
from ldk_athlete_ai_coach.main import app


@pytest.fixture()
def app_client() -> Generator[TestClient, None, None]:
    """Shared TestClient for API tests that do not override DB dependencies."""
    with TestClient(app) as tc:
        yield tc


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
