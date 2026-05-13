"""Extracted Notion schema for an Event page."""

from __future__ import annotations

from datetime import datetime

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_base import NotionBaseSchema
from ldk_athlete_ai_coach.domain.enums.event import (
    EventPlanRole,
    EventPriority,
    EventStatus,
    EventType,
)
from ldk_athlete_ai_coach.domain.enums.workout import WorkoutCategory


class NotionEvent(NotionBaseSchema):
    """Typed representation of a raw Notion Event database entry."""

    event_type: EventType
    sport: WorkoutCategory
    priority: EventPriority
    status: EventStatus
    role_in_plan: EventPlanRole | None = None
    target: str | None = None
    event_format: str | None = None
    target_time_seconds: int | None = None
    target_distance_km: float | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    location: str | None = None
    notes: str | None = None
    plan_notion_id: str | None = None
    race_workout_notion_id: str | None = None
    created_time: datetime | None = None
    last_edited_time: datetime | None = None
    archived: bool = False
    url: str | None = None
