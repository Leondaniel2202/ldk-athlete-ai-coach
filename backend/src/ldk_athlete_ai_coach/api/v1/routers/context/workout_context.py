"""Training-context endpoints for API v1."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.api.v1.schemas.workout_context import WorkoutContextResponse
from ldk_athlete_ai_coach.application.services.workout_context_service import WorkoutContextService
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.db.session import get_db_session

router = APIRouter(prefix="/workouts", tags=["workout_context"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/{workout_id}", response_model=WorkoutContextResponse)
def get_specific_workout_context(db: DbSession, workout_id: int) -> WorkoutContextResponse:
    """Return the current workout-centric training context snapshot."""
    service = WorkoutContextService(
        workout_repository=WorkoutRepository(db),
        session_repository=SessionRepository(db),
    )
    try:
        return service.get_specific_workout_context(workout_id=workout_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Workout not found") from exc
