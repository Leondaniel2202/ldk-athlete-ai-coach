"""Application settings management using pydantic-settings."""

from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ldk-athlete-ai-coach"
    app_env: str = "local"
    debug: bool = False

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int = 5432

    @computed_field # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        """Build SQLAlchemy connection URL from database environment variables."""
        return (
            "postgresql+psycopg://"
            f"{quote_plus(self.postgres_user)}:{quote_plus(self.postgres_password)}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings.

    Returns:
        Settings: Parsed application settings instance.
    """
    return Settings()  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]
