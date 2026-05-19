"""Pydantic response models for the training domain."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict

from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseDetailResponse


class PlanResponse(BaseModel):
    """Response schema for a single training plan."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    notion_page_id: str
    notion_url: str
    name: str
    description: str | None
    start_date: date
    end_date: date


class PlanDetailResponse(PlanResponse):
    """Extended response schema for a training plan with additional linked data."""

    phases: list[PhaseDetailResponse] = []


class PlanSummaryResponse(BaseModel):
    """Compact representation of a training plan."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    start_date: date
    end_date: date
