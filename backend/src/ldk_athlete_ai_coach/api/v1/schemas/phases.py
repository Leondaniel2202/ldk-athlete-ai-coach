"""Pydantic response models for the training domain."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict

from ldk_athlete_ai_coach.api.v1.schemas.workouts import (
    WorkoutDetailResponse,
)
from ldk_athlete_ai_coach.domain.enums.phase import PhaseFocusTag, PhaseType


class PhaseResponse(BaseModel):
    """Response schema for a single training phase."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    notion_page_id: str
    notion_url: str
    name: str
    description: str | None
    phase_type: PhaseType
    focus_tags: list[PhaseFocusTag]
    weekly_structure: str | None
    start_date: date
    end_date: date
    plan_id: int | None
    nutrition_guideline_id: int | None


class PhaseDetailResponse(PhaseResponse):
    """Extended response schema for a training phase with additional linked data."""

    workouts: list[WorkoutDetailResponse] = []


class PhaseSummaryResponse(BaseModel):
    """Compact representation of a training phase."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phase_type: PhaseType
    start_date: date
    end_date: date
