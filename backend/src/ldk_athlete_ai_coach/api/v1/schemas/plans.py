"""Pydantic response models for the training domain."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseDetailResponse


class PlanResponse(BaseModel):
    """Response schema for a single training plan."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    notion_page_id: str
    notion_url: str
    name: str
    plan_goal: str | None
    constraints: str | None
    rules_weekly_rhythm: str | None
    start_date_start: datetime | None
    start_date_end: datetime | None
    start_date_is_datetime: bool
    end_date_start: datetime | None
    end_date_end: datetime | None
    end_date_is_datetime: bool


class PlanDetailResponse(PlanResponse):
    """Extended response schema for a training plan with additional linked data."""

    phases: list[PhaseDetailResponse] = []


class PlanSummaryResponse(BaseModel):
    """Compact representation of a training plan."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    plan_goal: str | None
    start_date_start: datetime | None
    end_date_end: datetime | None
