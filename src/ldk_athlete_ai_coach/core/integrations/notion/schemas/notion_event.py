"""Extracted Notion schema for an Event page."""

from __future__ import annotations

from datetime import datetime

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_base import NotionBaseSchema


class NotionEvent(NotionBaseSchema):
    """Typed representation of a raw Notion Event database entry."""

    event_type: str | None = None
    target: str | None = None
    event_format: str | None = None
    notes: str | None = None
    priority: str | None = None
    start_date_start: datetime | None = None
    start_date_end: datetime | None = None
    start_date_is_datetime: bool = False
    end_date_start: datetime | None = None
    end_date_end: datetime | None = None
    end_date_is_datetime: bool = False
    place_name: str | None = None
    place_address: str | None = None
    place_latitude: float | None = None
    place_longitude: float | None = None
    place_google_place_id: str | None = None
    plan_notion_id: str | None = None
    race_workout_notion_id: str | None = None
    created_time: datetime | None = None
    last_edited_time: datetime | None = None
    archived: bool = False
    url: str | None = None
