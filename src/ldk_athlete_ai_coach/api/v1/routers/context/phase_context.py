"""Training-context endpoints for API v1."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.api.v1.schemas.phase_context import PhaseContextResponse
from ldk_athlete_ai_coach.application.services.phase_context_service import PhaseContextService
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.db.session import get_db_session

router = APIRouter(prefix="/phases", tags=["phase_context"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/{phase_id}", response_model=PhaseContextResponse)
def get_phase_context(db: DbSession, phase_id: int) -> PhaseContextResponse:
    """Return the current workout-centric training context snapshot."""
    service = PhaseContextService(
        phase_repository=PhaseRepository(db),
        workout_repository=WorkoutRepository(db),
        session_repository=SessionRepository(db),
    )
    return service.get_specific_phase_context(phase_id=phase_id)
