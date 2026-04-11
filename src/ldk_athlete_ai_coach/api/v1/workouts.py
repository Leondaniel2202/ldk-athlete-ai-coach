"""Workout endpoints for API v1."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.api.v1.schemas.training import (
    SessionResponse,
    WorkoutDetailResponse,
)
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.db.session import get_db_session

router = APIRouter(prefix="/workouts", tags=["workouts"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/{workout_id}", response_model=WorkoutDetailResponse)
def get_workout(
    workout_id: int,
    db: DbSession,
) -> WorkoutDetailResponse:
    """Retrieve a single workout by ID together with synced page content."""
    repo = WorkoutRepository(db)
    workout = repo.get_by_id(workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return WorkoutDetailResponse.model_validate(workout)


@router.get("/{workout_id}/sessions", response_model=list[SessionResponse])
def get_workout_sessions(
    workout_id: int,
    db: DbSession,
) -> list[SessionResponse]:
    """Retrieve all tracked sessions linked to a workout."""
    repo = WorkoutRepository(db)
    if repo.get_by_id(workout_id) is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    sessions = repo.get_sessions(workout_id)
    return [SessionResponse.model_validate(s) for s in sessions]
