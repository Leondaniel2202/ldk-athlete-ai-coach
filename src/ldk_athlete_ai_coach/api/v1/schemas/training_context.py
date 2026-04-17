"""Pydantic response models for the training-context endpoint."""

from __future__ import annotations

from pydantic import BaseModel

from ldk_athlete_ai_coach.api.v1.schemas.common import ContextMetadataResponse
from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseResponse
from ldk_athlete_ai_coach.api.v1.schemas.plans import PlanResponse
from ldk_athlete_ai_coach.api.v1.schemas.sessions import SessionResponse
from ldk_athlete_ai_coach.api.v1.schemas.workouts import WorkoutDetailResponse


class TrainingContextMetadataResponse(ContextMetadataResponse):
    """Response metadata for the training-context endpoint."""


class CurrentTrainingContextResponse(BaseModel):
    """Current plan and phase selection for the athlete."""

    plan: PlanResponse | None
    phase: PhaseResponse | None
    current_phase_week: int | None


class RecentWorkoutContextResponse(BaseModel):
    """A recent workout enriched with linked tracked sessions."""

    workout: WorkoutDetailResponse
    tracked_sessions: list[SessionResponse]


class AdherenceSummaryResponse(BaseModel):
    """Summary of adherence in the recent reporting window."""

    planned_workouts: int
    completed_workouts: int
    skipped_workouts: int
    completion_ratio: float | None


class TrainingContextResponse(BaseModel):
    """Aggregated response for the current training context endpoint."""

    metadata: TrainingContextMetadataResponse
    current: CurrentTrainingContextResponse
    planned_workouts: list[WorkoutDetailResponse]
    recent_workouts: list[RecentWorkoutContextResponse]
    adherence: AdherenceSummaryResponse
    data_gaps: list[str]


__all__ = [
    "AdherenceSummaryResponse",
    "CurrentTrainingContextResponse",
    "RecentWorkoutContextResponse",
    "TrainingContextMetadataResponse",
    "TrainingContextResponse",
]
