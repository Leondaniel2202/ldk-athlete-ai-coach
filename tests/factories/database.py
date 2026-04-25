"""Shared test database helpers.

Provides the test DB connection URL used by both integration and API fixtures.
Connection parameters are read from ``TEST_POSTGRES_*`` environment variables.

Default values match the ``postgres_test`` service in ``docker-compose.yml``
(port 5433, database ``ldk_athlete_ai_coach_test``, user ``postgres``, password ``postgres``).
"""

from __future__ import annotations

import os


def test_db_url() -> str:
    """Return the SQLAlchemy URL for the dedicated test Postgres database."""
    host = os.getenv("TEST_POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("TEST_POSTGRES_PORT", "5433")
    db = os.getenv("TEST_POSTGRES_DB", "ldk_athlete_ai_coach_test")
    user = os.getenv("TEST_POSTGRES_USER", "postgres")
    password = os.getenv("TEST_POSTGRES_PASSWORD", "postgres")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"
