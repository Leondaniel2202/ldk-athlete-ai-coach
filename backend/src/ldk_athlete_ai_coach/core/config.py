"""Application settings management using pydantic-settings."""

from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables and defaults."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = "ldk-athlete-ai-coach"
    app_env: str = "local"
    debug: bool = False

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int = 5432

    cors_allowed_origins: str = "http://localhost:3000"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    openai_timeout_seconds: int = 30

    @field_validator("debug", mode="before")
    @classmethod
    def _coerce_debug(cls, value: object) -> object:
        """Accept common environment-style debug values."""
        if not isinstance(value, str):
            return value

        normalized = value.strip().lower()
        if normalized in {"release", "prod", "production"}:
            return False
        if normalized in {"debug", "dev", "development", "local"}:
            return True
        return value

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        """Build SQLAlchemy connection URL from database environment variables.

        Returns:
            Fully qualified SQLAlchemy URL for the configured Postgres connection.

        """
        return (
            "postgresql+psycopg://"
            f"{quote_plus(self.postgres_user)}:{quote_plus(self.postgres_password)}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_allowed_origin_list(self) -> list[str]:
        """Return the configured CORS origins as a normalized list."""
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings.

    Returns:
        Settings: Parsed application settings instance.

    """
    return Settings()  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]
