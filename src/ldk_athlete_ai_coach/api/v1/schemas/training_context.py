"""Pydantic response models for the training domain."""

from __future__ import annotations

from pydantic import BaseModel

from ldk_athlete_ai_coach.api.v1.schemas.adherence import WorkoutAdherenceSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.common import ContextMetadataResponse
from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.plans import PlanSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.workouts import WorkoutContentResponse, WorkoutDetailResponse


class CurrentTrainingContextResponse(BaseModel):
    """Current plan/phase selection for the training-context endpoint."""

    plan_summary: PlanSummaryResponse | None
    phase_summary: PhaseSummaryResponse | None
    current_phase_week: int | None
    

class TrainingContextResponse(BaseModel):
    """Aggregated response for the current training context endpoint."""

    metadata: ContextMetadataResponse
    current: CurrentTrainingContextResponse
    planned_workouts: list[WorkoutContentResponse]
    recent_workouts: list[WorkoutDetailResponse]
    adherence: WorkoutAdherenceSummaryResponse
    data_gaps: list[str]