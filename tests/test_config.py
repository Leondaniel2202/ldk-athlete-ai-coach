"""Configuration loading and override behavior tests."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from ldk_athlete_ai_coach.core.config import Settings, get_settings


def test_settings_require_database_environment_values(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Ensure required database settings are provided via environment variables."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("POSTGRES_DB", raising=False)
    monkeypatch.delenv("POSTGRES_USER", raising=False)
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    monkeypatch.delenv("POSTGRES_HOST", raising=False)
    monkeypatch.delenv("POSTGRES_PORT", raising=False)

    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg] # pyright: ignore[reportCallIssue]


def test_settings_builds_database_url_from_component_values(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Ensure DB URL is derived from POSTGRES_* variables."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("POSTGRES_DB", "ldk_athlete_ai_coach")
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_PASSWORD", "postgres")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.delenv("POSTGRES_PORT", raising=False)

    settings = Settings()  # type: ignore[call-arg] # pyright: ignore[reportCallIssue]

    assert (
        settings.database_url
        == "postgresql+psycopg://postgres:postgres@localhost:5432/ldk_athlete_ai_coach"
    )


def test_get_settings_reads_environment_overrides(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Ensure cached settings reflect environment variable overrides."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APP_NAME", "test-app")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("POSTGRES_DB", "test_db")
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_PASSWORD", "postgres")
    monkeypatch.setenv("POSTGRES_HOST", "db")
    monkeypatch.setenv("POSTGRES_PORT", "5432")

    get_settings.cache_clear()
    settings = get_settings()

    assert settings.app_name == "test-app"
    assert settings.app_env == "test"
    assert settings.debug is True
    assert settings.database_url == "postgresql+psycopg://postgres:postgres@db:5432/test_db"

    get_settings.cache_clear()


def test_settings_default_openai_values_are_exposed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Ensure optional AI settings default cleanly when not configured."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("POSTGRES_DB", "ldk_athlete_ai_coach")
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_PASSWORD", "postgres")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("NOTION_API_KEY", "secret")
    monkeypatch.setenv("NOTION_PLAN_DATA_SOURCE_ID", "plan-ds")
    monkeypatch.setenv("NOTION_PHASE_DATA_SOURCE_ID", "phase-ds")
    monkeypatch.setenv("NOTION_NUTRITION_GUIDELINE_DATA_SOURCE_ID", "nutrition-ds")
    monkeypatch.setenv("NOTION_WORKOUT_DATA_SOURCE_ID", "workout-ds")
    monkeypatch.setenv("NOTION_EVENT_DATA_SOURCE_ID", "event-ds")
    monkeypatch.setenv("NOTION_SESSION_DATA_SOURCE_ID", "session-ds")
    monkeypatch.setenv("NOTION_FEEDBACK_DATA_SOURCE_ID", "feedback-ds")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_TIMEOUT_SECONDS", raising=False)

    settings = Settings()  # type: ignore[call-arg] # pyright: ignore[reportCallIssue]

    assert settings.openai_api_key is None
    assert settings.openai_model == "gpt-4.1-mini"
    assert settings.openai_timeout_seconds == 30


def test_settings_read_openai_overrides(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Ensure optional AI settings can be overridden via environment variables."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("POSTGRES_DB", "ldk_athlete_ai_coach")
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_PASSWORD", "postgres")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("NOTION_API_KEY", "secret")
    monkeypatch.setenv("NOTION_PLAN_DATA_SOURCE_ID", "plan-ds")
    monkeypatch.setenv("NOTION_PHASE_DATA_SOURCE_ID", "phase-ds")
    monkeypatch.setenv("NOTION_NUTRITION_GUIDELINE_DATA_SOURCE_ID", "nutrition-ds")
    monkeypatch.setenv("NOTION_WORKOUT_DATA_SOURCE_ID", "workout-ds")
    monkeypatch.setenv("NOTION_EVENT_DATA_SOURCE_ID", "event-ds")
    monkeypatch.setenv("NOTION_SESSION_DATA_SOURCE_ID", "session-ds")
    monkeypatch.setenv("NOTION_FEEDBACK_DATA_SOURCE_ID", "feedback-ds")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1")
    monkeypatch.setenv("OPENAI_TIMEOUT_SECONDS", "45")

    settings = Settings()  # type: ignore[call-arg] # pyright: ignore[reportCallIssue]

    assert settings.openai_api_key == "sk-test"
    assert settings.openai_model == "gpt-4.1"
    assert settings.openai_timeout_seconds == 45
