"""Extracted Notion schema for a Workout page."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class NotionWorkout(BaseModel):
    """Typed representation of a raw Notion Workout database entry.

    Fields map to the columns defined in
    :class:`~ldk_athlete_ai_coach.db.models.sport_manager.Workout`.
    """

    notion_id: str
    name: str
    date_start: datetime | None = None
    date_end: datetime | None = None
    date_is_datetime: bool = False
    category: str | None = None
    difficulty: str | None = None
    equipment: list[str] = Field(default_factory=list)
    impact: str | None = None
    metrics_to_record: list[str] = Field(default_factory=list)
    purpose: list[str] = Field(default_factory=list)
    primarily_used_muscle_group: list[str] = Field(default_factory=list)
    planned_distance_km: float | None = None
    planned_duration_min: float | None = None
    planned_rpe: float | None = None
    planned_week_number: float | None = None
    actual_rpe: float | None = None
    additional_info: str | None = None
    cancelled: bool = False
    skipped: bool = False
    phase_notion_id: str | None = None
    created_time: datetime | None = None
    last_edited_time: datetime | None = None
    archived: bool = False
    url: str | None = None
