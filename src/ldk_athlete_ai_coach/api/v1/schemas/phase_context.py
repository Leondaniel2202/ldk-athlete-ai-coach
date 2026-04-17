"""Pydantic response models for the training domain."""

from __future__ import annotations

from pydantic import BaseModel

from ldk_athlete_ai_coach.api.v1.schemas.adherence import WorkoutAdherenceSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.common import ContextMetadataResponse
from ldk_athlete_ai_coach.api.v1.schemas.metrics import (
    WeeklyMetricsResponse,
)
from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseResponse
from ldk_athlete_ai_coach.api.v1.schemas.plans import PlanSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.workouts import (
    WorkoutContentResponse,
    WorkoutDetailResponse,
)
from ldk_athlete_ai_coach.domain.enums.status import PhaseStatus


class PhaseContextResponse(BaseModel):
    """Response schema for a specific phase training context."""

    metadata: ContextMetadataResponse
    plan_summary: PlanSummaryResponse | None
    phase_status: PhaseStatus
    phase: PhaseResponse
    open_workouts: list[WorkoutContentResponse]
    done_workouts: list[WorkoutDetailResponse]
    weekly_metrics: list[WeeklyMetricsResponse]
    adherence: WorkoutAdherenceSummaryResponse
    data_gaps: list[str]
