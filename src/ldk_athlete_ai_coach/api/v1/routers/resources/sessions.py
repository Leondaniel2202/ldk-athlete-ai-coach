"""Session endpoints for API v1."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.api.v1.schemas.sessions import SessionResponse, SessionSummaryResponse
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.session import get_db_session

router = APIRouter(prefix="/sessions", tags=["sessions"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/recent", response_model=list[SessionResponse])
def get_recent_sessions(
    db: DbSession,
    days: Annotated[int, Query(ge=1, description="Look-back window in days")] = 14,
) -> list[SessionResponse]:
    """Retrieve tracked sessions from the last *days* days."""
    repo = SessionRepository(db)
    sessions = repo.list_recent(days)
    return [SessionResponse.model_validate(s) for s in sessions]


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: int,
    db: DbSession,
) -> SessionResponse:
    """Retrieve a single tracked session by ID.

    Args:
        session_id: Primary key of the tracked session.
        db: Injected database session.

    Returns:
        SessionResponse: The session data.

    Raises:
        HTTPException: 404 if the session does not exist.

    """
    repo = SessionRepository(db)
    session = repo.get_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse.model_validate(session)


@router.get("{session_id}/summary", response_model=SessionSummaryResponse)
def get_session_summary(
    session_id: int,
    db: DbSession,
) -> SessionSummaryResponse:
    """Retrieve a summary of a tracked session, including key metrics and workout context."""
    repo = SessionRepository(db)
    session = repo.get_by_id(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionSummaryResponse.model_validate(session)
