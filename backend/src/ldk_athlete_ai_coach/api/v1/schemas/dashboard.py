"""Dashboard response schemas for API v1."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.plans import PlanSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.workouts import WorkoutSummaryResponse


class OverviewItemResponse(BaseModel):
    """Single high-level dashboard overview item."""

    label: str
    value: str | None
    detail: str | None


class DashboardDataResponse(BaseModel):
    """Dashboard start page response."""

    athlete_name: str
    summary: str
    next_action: str
    overview: list[OverviewItemResponse]
    current_plan: PlanSummaryResponse | None = None
    current_phase: PhaseSummaryResponse | None = None
    weekly_outlook: list[WorkoutSummaryResponse]

    model_config = ConfigDict(from_attributes=True)
