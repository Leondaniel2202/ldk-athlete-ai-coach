"""Database engine and session factory configuration."""

from collections.abc import Generator
from functools import lru_cache
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ldk_athlete_ai_coach.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """Return the shared SQLAlchemy engine for the configured database."""
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    """Return the shared SQLAlchemy session factory."""
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=get_engine(),
        class_=Session,
    )


def get_db_session() -> Generator[Session, Any, None]:
    """Yield a database session for a request scope.

    Yields:
        Session: Active SQLAlchemy session.

    """
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def __getattr__(name: str) -> Engine | sessionmaker[Session]:
    """Provide lazy compatibility aliases for legacy engine/session imports."""
    if name == "engine":
        return get_engine()
    if name == "SessionLocal":
        return get_session_factory()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
