"""Pydantic response models for the training domain."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PhaseResponse(BaseModel):
    """Response schema for a single training phase."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    notion_page_id: str
    notion_url: str
    name: str
    notes: str | None
    phase_type: str | None
    focus_tags: list[str]
    weekly_structure: str | None
    timeframe_start: datetime | None
    timeframe_end: datetime | None
    timeframe_is_datetime: bool
    plan_id: int | None
    nutrition_guideline_id: int | None
    

class PhaseSummaryResponse(BaseModel):
    """Compact representation of a training phase."""
    
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phase_type: str | None
    timeframe_start: datetime | None
    timeframe_end: datetime | None