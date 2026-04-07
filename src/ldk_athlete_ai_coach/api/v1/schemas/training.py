"""Pydantic response models for the training domain (Phase → Workout → Session)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PhaseResponse(BaseModel):
    """Response schema for a single Phase."""

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


class WorkoutResponse(BaseModel):
    """Response schema for a single Workout."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    notion_page_id: str
    notion_url: str
    name: str
    date_start: datetime | None
    date_end: datetime | None
    date_is_datetime: bool
    category: str | None
    difficulty: str | None
    equipment: list[str]
    impact: str | None
    metrics_to_record: list[str]
    purpose: list[str]
    primarily_used_muscle_group: list[str]
    planned_distance_km: float | None
    planned_duration_min: float | None
    planned_rpe: float | None
    planned_week_number: float | None
    actual_rpe: float | None
    additional_info: str | None
    cancelled: bool
    skipped: bool
    phase_id: int | None


class SessionResponse(BaseModel):
    """Response schema for a single TrackedSession."""

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
