"""Factory helpers for building Settings instances in tests."""

from __future__ import annotations

from typing import Any

from ldk_athlete_ai_coach.core.config import Settings


def make_settings(**overrides: Any) -> Settings:
    """Build a minimal Settings instance with required fields populated.

    Postgres fields are pre-filled with test placeholders.
    Pass keyword arguments to override individual fields.
    """
    defaults: dict[str, Any] = {
        "postgres_db": "ldk_athlete_ai_coach_test",
        "postgres_user": "postgres",
        "postgres_password": "postgres",
        "postgres_host": "127.0.0.1",
        "postgres_port": 5433,
    }
    defaults.update(overrides)
    return Settings(**defaults)  # pyright: ignore[reportCallIssue]
