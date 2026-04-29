"""Pydantic response models for the training domain."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from ldk_athlete_ai_coach.api.v1.schemas.sessions import SessionResponse
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus
from ldk_athlete_ai_coach.domain.enums.workout import WorkoutCategory


class WorkoutResponse(BaseModel):
    """Response schema for a workout."""

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
    planned_training_load: float | None
    planned_week_number: float | None
    actual_duration_min: float | None
    actual_distance_km: float | None
    actual_training_load: float | None
    actual_calories_burned_kcal: float | None
    weighted_hrr_intensity_sum: float | None
    actual_hrr_intensity: float | None
    actual_rpe: float | None
    done_date_start: datetime | None
    done_date_end: datetime | None
    done_date_is_datetime: bool
    status: str | None
    training_load_method: str | None
    additional_info: str | None
    cancelled: bool
    skipped: bool
    phase_id: int | None


class WorkoutContentResponse(WorkoutResponse):
    """Response schema for a workout, including the content of the Notion page.
    Includes all fields from :class:`WorkoutResponse`."""

    notion_page_content: str | None


class WorkoutDetailResponse(WorkoutContentResponse):
    """Response schema for a workout, including linked tracked sessions.
    Includes all fields from :class:`WorkoutContentResponse`."""

    tracked_sessions: list[SessionResponse]


class WorkoutSummaryResponse(BaseModel):
    """Compact representation of a workout."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: WorkoutCategory | None
    date_start: datetime | None
    done_date_start: datetime | None
    status: WorkoutStatus
