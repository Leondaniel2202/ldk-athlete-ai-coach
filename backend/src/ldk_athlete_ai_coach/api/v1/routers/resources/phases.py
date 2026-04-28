"""Phase endpoints for API v1."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseResponse, PhaseSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.workouts import WorkoutResponse
from ldk_athlete_ai_coach.db.models.training import Workout
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.db.session import get_db_session

router = APIRouter(prefix="/phases", tags=["phases"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/current", response_model=PhaseResponse)
def get_current_phase(
    db: DbSession,
) -> PhaseResponse:
    """Retrieve the currently active phase.

    Args:
        db: Injected database session.

    Returns:
        PhaseResponse: The phase data.

    Raises:
        HTTPException: 404 if the phase does not exist.

    """
    repo = PhaseRepository(db)
    phase = repo.get_active(now=datetime.now(tz=UTC))
    if phase is None:
        raise HTTPException(status_code=404, detail="Phase not found")
    return PhaseResponse.model_validate(phase)


@router.get("/{phase_id}", response_model=PhaseResponse)
def get_phase(
    phase_id: int,
    db: DbSession,
) -> PhaseResponse:
    """Retrieve a single phase by ID.

    Args:
        phase_id: Primary key of the phase.
        db: Injected database session.

    Returns:
        PhaseResponse: The phase data.

    Raises:
        HTTPException: 404 if the phase does not exist.

    """
    repo = PhaseRepository(db)
    phase = repo.get_by_id(phase_id)
    if phase is None:
        raise HTTPException(status_code=404, detail="Phase not found")
    return PhaseResponse.model_validate(phase)


@router.get("/{phase_id}/workouts", response_model=list[WorkoutResponse])
def get_phase_workouts(
    phase_id: int,
    db: DbSession,
) -> list[WorkoutResponse]:
    """Retrieve all workouts belonging to a phase.

    Args:
        phase_id: Primary key of the phase.
        db: Injected database session.

    Returns:
        list[WorkoutResponse]: Workouts linked to the phase.

    Raises:
        HTTPException: 404 if the phase does not exist.

    """
    phase_repo = PhaseRepository(db)
    workout_repo = WorkoutRepository(db)
    if phase_repo.get_by_id(phase_id) is None:
        raise HTTPException(status_code=404, detail="Phase not found")
    workouts: list[Workout] = workout_repo.list_by_phase_id(phase_id)
    return [WorkoutResponse.model_validate(w) for w in workouts]


@router.get("/{phase_id}/summary", response_model=PhaseSummaryResponse)
def get_phase_summary(
    phase_id: int,
    db: DbSession,
) -> PhaseSummaryResponse:
    """Retrieve a summary of a phase, including key dates and metrics."""
    repo = PhaseRepository(db)
    phase = repo.get_by_id(phase_id)
    if phase is None:
        raise HTTPException(status_code=404, detail="Phase not found")
    return PhaseSummaryResponse.model_validate(phase)
