from functools import lru_cache

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

    postgres_db: str = "ldk_athlete_ai_coach"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/ldk_athlete_ai_coach"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
