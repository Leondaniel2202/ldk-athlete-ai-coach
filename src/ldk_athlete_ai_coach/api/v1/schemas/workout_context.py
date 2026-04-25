"""Pydantic response models for the training domain."""

from __future__ import annotations

from pydantic import BaseModel

from ldk_athlete_ai_coach.api.v1.schemas.common import ContextMetadataResponse
from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.plans import PlanSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.workouts import WorkoutDetailResponse
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus


class WorkoutContextResponse(BaseModel):
    """Aggregated response for a specific workout context, combining workout details with
    the phase/plan context."""

    metadata: ContextMetadataResponse
    plan_summary: PlanSummaryResponse | None
    phase_summary: PhaseSummaryResponse | None
    workout_status: WorkoutStatus
    workout_details: WorkoutDetailResponse
