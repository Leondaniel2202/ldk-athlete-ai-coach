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
