"""Database engine and session factory configuration."""

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ldk_athlete_ai_coach.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)


def get_db_session() -> Generator[Session, Any, None]:
    """Yield a database session for a request scope.

    Yields:
        Session: Active SQLAlchemy session.

    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
