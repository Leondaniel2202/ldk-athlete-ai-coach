"""Pydantic response schemas for the training domain."""

from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseResponse
from ldk_athlete_ai_coach.api.v1.schemas.plans import PlanResponse
from ldk_athlete_ai_coach.api.v1.schemas.sessions import SessionResponse
from ldk_athlete_ai_coach.api.v1.schemas.workouts import WorkoutDetailResponse

__all__ = [
    "PhaseResponse",
    "PlanResponse",
    "SessionResponse",
    "WorkoutDetailResponse",
]
