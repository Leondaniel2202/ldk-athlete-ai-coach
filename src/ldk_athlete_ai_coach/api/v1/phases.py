"""Phase endpoints for API v1."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.api.v1.schemas.training import PhaseResponse, WorkoutResponse
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.session import get_db_session

router = APIRouter(prefix="/phases", tags=["phases"])

DbSession = Annotated[Session, Depends(get_db_session)]


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
    repo = PhaseRepository(db)
    if repo.get_by_id(phase_id) is None:
        raise HTTPException(status_code=404, detail="Phase not found")
    workouts = repo.get_workouts(phase_id)
    return [WorkoutResponse.model_validate(w) for w in workouts]
