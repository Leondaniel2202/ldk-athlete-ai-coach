"""Workout endpoints for API v1."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.api.v1.schemas.training import SessionResponse, WorkoutResponse
from ldk_athlete_ai_coach.db.session import get_db_session
from ldk_athlete_ai_coach.domain.services.workout_service import WorkoutService

router = APIRouter(prefix="/workouts", tags=["workouts"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/{workout_id}", response_model=WorkoutResponse)
def get_workout(
    workout_id: int,
    db: DbSession,
) -> WorkoutResponse:
    """Retrieve a single workout by ID.

    Args:
        workout_id: Primary key of the workout.
        db: Injected database session.

    Returns:
        WorkoutResponse: The workout data.

    Raises:
        HTTPException: 404 if the workout does not exist.
    """
    service = WorkoutService(db)
    workout = service.get_workout(workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return WorkoutResponse.model_validate(workout)


@router.get("/{workout_id}/sessions", response_model=list[SessionResponse])
def get_workout_sessions(
    workout_id: int,
    db: DbSession,
) -> list[SessionResponse]:
    """Retrieve all tracked sessions linked to a workout.

    Args:
        workout_id: Primary key of the workout.
        db: Injected database session.

    Returns:
        list[SessionResponse]: Sessions linked to the workout.

    Raises:
        HTTPException: 404 if the workout does not exist.
    """
    service = WorkoutService(db)
    if service.get_workout(workout_id) is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    sessions = service.get_workout_sessions(workout_id)
    return [SessionResponse.model_validate(s) for s in sessions]
