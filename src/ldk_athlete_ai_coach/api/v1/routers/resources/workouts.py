"""Workout endpoints for API v1."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.api.v1.schemas.sessions import SessionResponse
from ldk_athlete_ai_coach.api.v1.schemas.workouts import (
    WorkoutContentResponse,
    WorkoutDetailResponse,
    WorkoutResponse,
)
from ldk_athlete_ai_coach.db.models.training import TrackedSession
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.db.session import get_db_session

router = APIRouter(prefix="/workouts", tags=["workouts"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/{workout_id}", response_model=WorkoutDetailResponse)
def get_workout(
    workout_id: int,
    db: DbSession,
) -> WorkoutResponse:
    """Retrieve a single workout by ID together with synced page content."""
    repo = WorkoutRepository(db)
    workout = repo.get_by_id(workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return WorkoutDetailResponse.model_validate(workout)


@router.get("/{workout_id}/content", response_model=WorkoutContentResponse)
def get_workout_content(
    workout_id: int,
    db: DbSession,
) -> WorkoutContentResponse:
    """Retrieve a single workout by ID together with synced page content."""
    repo = WorkoutRepository(db)
    workout = repo.get_by_id(workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return WorkoutDetailResponse.model_validate(workout)


@router.get("/{workout_id}/details", response_model=WorkoutDetailResponse)
def get_workout_details(
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
    workout_repo = WorkoutRepository(db)
    session_repo = SessionRepository(db)
    if workout_repo.get_by_id(workout_id) is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    sessions: list[TrackedSession] = session_repo.list_by_workout_id(workout_id)
    return [SessionResponse.model_validate(s) for s in sessions]
