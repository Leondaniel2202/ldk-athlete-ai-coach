"""Pydantic response models for the training domain."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from ldk_athlete_ai_coach.api.v1.schemas.adherence import WorkoutAdherenceSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.common import ContextMetadataResponse
from ldk_athlete_ai_coach.api.v1.schemas.metrics import (
    TrainingMetricsResponse,
)
from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseResponse, PhaseSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.plans import PlanSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.workouts import (
    WorkoutContentResponse,
    WorkoutDetailResponse,
)
from ldk_athlete_ai_coach.domain.enums.status import PhaseStatus


class PhaseContextResponse(BaseModel):
    """Response schema for a specific phase training context."""

    metadata: ContextMetadataResponse
    plan_summary: PlanSummaryResponse
    phase_status: PhaseStatus
    phase: PhaseResponse
    open_workouts: list[WorkoutContentResponse]
    done_workouts: list[WorkoutDetailResponse]
    weekly_metrics: list[TrainingMetricsResponse]
    adherence: WorkoutAdherenceSummaryResponse
    data_gaps: list[str]


class PhaseWeekContextMetadataResponse(ContextMetadataResponse):
    """Metadata for a specific phase week training context."""

    phase_week_number: int
    phase_week_start_date: datetime
    phase_week_end_date: datetime


class PhaseWeekContextResponse(BaseModel):
    """Response schema for a specific phase week training context."""

    metadata: PhaseWeekContextMetadataResponse
    plan_summary: PlanSummaryResponse
    phase_status: PhaseStatus
    phase_summary: PhaseSummaryResponse
    workouts: list[WorkoutDetailResponse]
    metrics: TrainingMetricsResponse
    adherence: WorkoutAdherenceSummaryResponse
    data_gaps: list[str]
