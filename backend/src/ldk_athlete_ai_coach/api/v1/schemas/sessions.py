"""Pydantic response models for the training domain."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionResponse(BaseModel):
    """Response schema for a tracked workout session."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    notion_page_id: str
    notion_url: str
    name: str
    source: str | None
    session_type: str | None
    external_id: str | None
    start_start: datetime | None
    start_end: datetime | None
    start_is_datetime: bool
    end_start: datetime | None
    end_end: datetime | None
    end_is_datetime: bool
    active_energy_kj: float | None
    active_energy_burned_kj: float | None
    avg_hr: float | None
    max_hr: float | None
    calories_kcal: float | None
    distance_km: float | None
    duration_min: float | None
    elevation_ascended_m: float | None
    elevation_descended_m: float | None
    intensity_kcal_per_hr_kg: float | None
    step_cadence_count_per_min: float | None
    steps: float | None
    workout_id: int | None


class SessionSummaryResponse(BaseModel):
    """Compact representation of a tracked workout session."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    source: str | None
    session_type: str | None
    start_start: datetime | None
    end_end: datetime | None
