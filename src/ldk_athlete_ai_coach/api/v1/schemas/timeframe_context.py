"""Pydantic response models for the training-context endpoint."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from ldk_athlete_ai_coach.api.v1.schemas.adherence import WorkoutAdherenceSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.common import ContextMetadataResponse
from ldk_athlete_ai_coach.api.v1.schemas.metrics import TrainingMetricsResponse
from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.plans import PlanSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.workouts import (
    WorkoutContentResponse,
    WorkoutDetailResponse,
)
from ldk_athlete_ai_coach.domain.enums.status import TimeframeStatus


class TimeframeMetadataResponse(ContextMetadataResponse):
    """Additional metadata fields specific to timeframe contexts."""

    timeframe_status: TimeframeStatus
    timeframe_start: datetime
    timeframe_end: datetime


class TimeframeContextResponse(BaseModel):
    """Aggregated response for a specific timeframe context, combining workout details with
    summaries of the involved phases/plans."""

    metadata: TimeframeMetadataResponse
    plans: list[PlanSummaryResponse]
    phases: list[PhaseSummaryResponse]
    open_workouts: list[WorkoutContentResponse]
    done_workouts: list[WorkoutDetailResponse]
    metrics: TrainingMetricsResponse
    adherence: WorkoutAdherenceSummaryResponse
    data_gaps: list[str]


__all__ = [
    "TimeframeContextResponse",
    "TimeframeMetadataResponse",
]
