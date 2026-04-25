"""Training-context endpoints for API v1."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.api.v1.schemas.phase_context import (
    PhaseContextResponse,
    PhaseWeekContextResponse,
)
from ldk_athlete_ai_coach.application.services.phase_context_service import PhaseContextService
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.db.session import get_db_session

router = APIRouter(prefix="/phases", tags=["phase_context"])

DbSession = Annotated[Session, Depends(get_db_session)]


def _phase_context_http_error(exc: ValueError) -> HTTPException:
    """Convert service-layer missing-phase errors into an API exception."""
    if str(exc) == "Phase not found":
        return HTTPException(status_code=404, detail="Phase not found")
    return HTTPException(status_code=500, detail=str(exc))


@router.get("/{phase_id}", response_model=PhaseContextResponse)
def get_specific_phase_context(db: DbSession, phase_id: int) -> PhaseContextResponse:
    """Return the current workout-centric training context snapshot."""
    service = PhaseContextService(
        phase_repository=PhaseRepository(db),
        workout_repository=WorkoutRepository(db),
        session_repository=SessionRepository(db),
    )
    try:
        return service.get_specific_phase_context(phase_id=phase_id)
    except ValueError as exc:
        raise _phase_context_http_error(exc) from exc


@router.get("/{phase_id}/weeks", response_model=PhaseWeekContextResponse)
def get_phase_week_context(
    db: DbSession,
    phase_id: int,
    week_start_date: Annotated[
        datetime,
        Query(description="Start date of the week to retrieve, in ISO format (YYYY-MM-DD)"),
    ],
) -> PhaseWeekContextResponse:
    """Return the current workout-centric training context snapshot."""
    service = PhaseContextService(
        phase_repository=PhaseRepository(db),
        workout_repository=WorkoutRepository(db),
        session_repository=SessionRepository(db),
    )
    try:
        return service.get_specific_phase_week_context(
            phase_id=phase_id, week_start_date=week_start_date
        )
    except ValueError as exc:
        raise _phase_context_http_error(exc) from exc
