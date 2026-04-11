"""Application settings management using pydantic-settings."""

from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import AliasChoices, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
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

    # Notion integration. The public API now queries data sources rather than the
    # old single-source database query endpoint, but the legacy *_DB_ID env vars
    # are still accepted so existing local setups keep working during migration.
    notion_api_key: str
    notion_phase_data_source_id: str = Field(
        validation_alias=AliasChoices("NOTION_PHASE_DATA_SOURCE_ID", "NOTION_PHASE_DB_ID")
    )
    notion_workout_data_source_id: str = Field(
        validation_alias=AliasChoices("NOTION_WORKOUT_DATA_SOURCE_ID", "NOTION_WORKOUT_DB_ID")
    )
    notion_session_data_source_id: str = Field(
        validation_alias=AliasChoices("NOTION_SESSION_DATA_SOURCE_ID", "NOTION_SESSION_DB_ID")
    )
    notion_feedback_data_source_id: str = Field(
        validation_alias=AliasChoices(
            "NOTION_FEEDBACK_DATA_SOURCE_ID",
            "NOTION_FEEDBACK_DB_ID",
        )
    )

    notion_page_size: int = 100
    notion_timeout_seconds: int = 30
    notion_max_retries: int = 3

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


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings.

    Returns:
        Settings: Parsed application settings instance.
    """
    return Settings()  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]
