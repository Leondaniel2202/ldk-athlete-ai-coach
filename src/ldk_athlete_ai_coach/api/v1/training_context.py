"""Training-context endpoints for API v1."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.api.v1.schemas.training import TrainingContextResponse
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.plan_repository import PlanRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.db.session import get_db_session
from ldk_athlete_ai_coach.domain.services.training_context_service import TrainingContextService

router = APIRouter(prefix="/training-context", tags=["training-context"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/current", response_model=TrainingContextResponse)
def get_current_training_context(db: DbSession) -> TrainingContextResponse:
    """Return the current workout-centric training context snapshot."""
    service = TrainingContextService(
        plan_repository=PlanRepository(db),
        phase_repository=PhaseRepository(db),
        workout_repository=WorkoutRepository(db),
        session_repository=SessionRepository(db),
    )
    return service.get_current_context()
