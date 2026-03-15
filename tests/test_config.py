"""Configuration loading and override behavior tests."""
import pytest

from ldk_athlete_ai_coach.core.config import Settings, get_settings


def test_settings_use_default_values_when_environment_is_missing(
    monkeypatch,
) -> None:
    """Ensure defaults are used when relevant environment variables are absent."""
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = Settings(_env_file=None)

    assert settings.app_name == "ldk-athlete-ai-coach"
    assert settings.app_env == "local"
    assert settings.debug is False
    assert (
        settings.database_url
        == "postgresql+psycopg://postgres:postgres@localhost:5432/ldk_athlete_ai_coach"
    )


def test_get_settings_reads_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure cached settings reflect environment variable overrides."""
    monkeypatch.setenv("APP_NAME", "test-app")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@db:5432/test_db",
    )

    get_settings.cache_clear()
    settings = get_settings()

    assert settings.app_name == "test-app"
    assert settings.app_env == "test"
    assert settings.debug is True
    assert settings.database_url == "postgresql+psycopg://postgres:postgres@db:5432/test_db"

    get_settings.cache_clear()
