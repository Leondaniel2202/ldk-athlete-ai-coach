"""Public AI endpoints for API v1."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.ai.errors import AIConfigurationError, AIProviderError
from ldk_athlete_ai_coach.ai.llm.openai_client import OpenAIClient
from ldk_athlete_ai_coach.ai.services.current_context_analysis import (
    AnalyzeCurrentContextService,
)
from ldk_athlete_ai_coach.api.v1.schemas.ai import (
    AnalyzeCurrentContextRequest,
    AnalyzeCurrentContextResponse,
)
from ldk_athlete_ai_coach.application.services.training_context_service import (
    TrainingContextService,
)
from ldk_athlete_ai_coach.core.config import get_settings
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.plan_repository import PlanRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.db.session import get_db_session

router = APIRouter(prefix="/ai", tags=["ai"])

DbSession = Annotated[Session, Depends(get_db_session)]


def build_analyze_current_context_service(db: Session) -> AnalyzeCurrentContextService:
    """Construct the AI current-context service from the active DB session."""
    settings = get_settings()
    llm_client = OpenAIClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        timeout_seconds=settings.openai_timeout_seconds,
    )
    training_context_service = TrainingContextService(
        plan_repository=PlanRepository(db),
        phase_repository=PhaseRepository(db),
        workout_repository=WorkoutRepository(db),
        session_repository=SessionRepository(db),
    )
    return AnalyzeCurrentContextService(training_context_service, llm_client)


@router.post("/analyze-current-context", response_model=AnalyzeCurrentContextResponse)
def analyze_current_context(
    db: DbSession,
    payload: AnalyzeCurrentContextRequest | None = None,
) -> AnalyzeCurrentContextResponse:
    """Analyze the current training context through the AI layer."""
    request = payload or AnalyzeCurrentContextRequest()
    try:
        service = build_analyze_current_context_service(db)
        return service.analyze_current_context(request.instruction)
    except (AIConfigurationError, AIProviderError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
