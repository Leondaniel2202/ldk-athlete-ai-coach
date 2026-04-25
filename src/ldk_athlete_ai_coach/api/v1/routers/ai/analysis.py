"""AI endpoints for API v1."""

from __future__ import annotations

from typing import Annotated, Literal, overload

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.ai.errors import AIConfigurationError, AIProviderError
from ldk_athlete_ai_coach.ai.llm.openai_client import OpenAIClient
from ldk_athlete_ai_coach.ai.services.phase_context_analysis import AnalyzePhaseContextService
from ldk_athlete_ai_coach.ai.services.workout_context_analysis import AnalyzeWorkoutContextService
from ldk_athlete_ai_coach.api.v1.schemas.ai import (
    AnalyzePhaseContextRequest,
    AnalyzePhaseContextResponse,
    AnalyzeWorkoutContextRequest,
    AnalyzeWorkoutContextResponse,
)
from ldk_athlete_ai_coach.application.services.phase_context_service import PhaseContextService
from ldk_athlete_ai_coach.application.services.workout_context_service import WorkoutContextService
from ldk_athlete_ai_coach.core.config import get_settings
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.db.session import get_db_session

router = APIRouter(prefix="/analysis", tags=["ai"])

DbSession = Annotated[Session, Depends(get_db_session)]


@overload
def build_analyze_context_service(
    db: Session, context: Literal["phase_context"]
) -> AnalyzePhaseContextService: ...


@overload
def build_analyze_context_service(
    db: Session, context: Literal["workout_context"]
) -> AnalyzeWorkoutContextService: ...


def build_analyze_context_service(
    db: Session, context: Literal["phase_context", "workout_context"]
) -> AnalyzePhaseContextService | AnalyzeWorkoutContextService:
    """Construct the current-context AI service from DB and app settings."""
    settings = get_settings()
    llm_client = OpenAIClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        timeout_seconds=settings.openai_timeout_seconds,
    )
    context_services: dict[str, AnalyzePhaseContextService | AnalyzeWorkoutContextService] = {
        "phase_context": AnalyzePhaseContextService(
            PhaseContextService(
                phase_repository=PhaseRepository(db),
                workout_repository=WorkoutRepository(db),
                session_repository=SessionRepository(db),
            ),
            llm_client=llm_client,
        ),
        "workout_context": AnalyzeWorkoutContextService(
            WorkoutContextService(
                workout_repository=WorkoutRepository(db),
                session_repository=SessionRepository(db),
            ),
            llm_client=llm_client,
        ),
    }
    return context_services[context]


@router.post("/specific-phase-context/{phase_id}", response_model=AnalyzePhaseContextResponse)
def analyze_specific_phase_context(
    db: DbSession,
    phase_id: int,
    payload: AnalyzePhaseContextRequest | None = None,
) -> AnalyzePhaseContextResponse:
    """Analyze the current training context through the AI layer."""
    request: AnalyzePhaseContextRequest = payload or AnalyzePhaseContextRequest()
    try:
        service: AnalyzePhaseContextService = build_analyze_context_service(
            db,
            context="phase_context",
        )
        return service.analyze_phase_context(
            phase_id=phase_id,
            instruction=request.instruction,
        )
    except (AIConfigurationError, AIProviderError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/specific-workout-context/{workout_id}", response_model=AnalyzeWorkoutContextResponse)
def analyze_specific_workout_context(
    db: DbSession,
    workout_id: int,
    payload: AnalyzeWorkoutContextRequest | None = None,
) -> AnalyzeWorkoutContextResponse:
    """Analyze the current training context through the AI layer."""
    request: AnalyzeWorkoutContextRequest = payload or AnalyzeWorkoutContextRequest()
    try:
        service: AnalyzeWorkoutContextService = build_analyze_context_service(
            db,
            context="workout_context",
        )
        return service.analyze_specific_workout_context(
            workout_id=workout_id,
            instruction=request.instruction,
        )
    except (AIConfigurationError, AIProviderError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
