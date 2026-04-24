"""Factory helpers for building Settings instances in tests."""

from __future__ import annotations

from typing import Any

from ldk_athlete_ai_coach.core.config import Settings


def make_settings(**overrides: Any) -> Settings:
    """Build a minimal Settings instance with required fields populated.

    All Notion and Postgres fields are pre-filled with test placeholders.
    Pass keyword arguments to override individual fields.
    """
    defaults: dict[str, Any] = {
        "postgres_db": "test_db",
        "postgres_user": "postgres",
        "postgres_password": "postgres",
        "postgres_host": "localhost",
        "postgres_port": 5432,
        "notion_api_key": "secret_test_key",
        "notion_plan_data_source_id": "plan-data-source-id",
        "notion_phase_data_source_id": "phase-data-source-id",
        "notion_nutrition_guideline_data_source_id": "nutrition-data-source-id",
        "notion_workout_data_source_id": "workout-data-source-id",
        "notion_event_data_source_id": "event-data-source-id",
        "notion_session_data_source_id": "session-data-source-id",
        "notion_feedback_data_source_id": "feedback-data-source-id",
        "notion_page_size": 100,
        "notion_timeout_seconds": 30,
        "notion_max_retries": 3,
    }
    defaults.update(overrides)
    return Settings(**defaults)  # pyright: ignore[reportCallIssue]
