"""Extracted Notion schema for a Workout page."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_base import NotionBaseSchema
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus


class NotionWorkout(NotionBaseSchema):
    """Typed representation of a raw Notion Workout database entry.

    Inherits common Notion identity fields from :class:`NotionBaseSchema`.
    The remaining fields map to the columns defined in
    :class:`~ldk_athlete_ai_coach.db.models.training.Workout`.
    """

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
    planned_training_load: float | None = None
    planned_calendar_week: float | None = None
    actual_duration_min: float | None = None
    actual_distance_km: float | None = None
    actual_training_load: float | None = None
    actual_calories_burned_kcal: float | None = None
    weighted_hrr_intensity_sum: float | None = None
    actual_hrr_intensity: float | None = None
    actual_rpe: float | None = None
    done_date_start: datetime | None = None
    done_date_end: datetime | None = None
    done_date_is_datetime: bool = False
    status: WorkoutStatus | None = None
    training_load_method: str | None = None
    additional_info: str | None = None
    cancelled: bool = False
    skipped: bool = False
    phase_notion_id: str | None = None
    created_time: datetime | None = None
    last_edited_time: datetime | None = None
    archived: bool = False
    url: str | None = None
