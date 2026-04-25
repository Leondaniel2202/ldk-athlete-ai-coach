"""Extracted Notion schema for a Plan page."""

from __future__ import annotations

from datetime import datetime

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_base import NotionBaseSchema


class NotionPlan(NotionBaseSchema):
    """Typed representation of a raw Notion Plan database entry."""

    plan_goal: str | None = None
    constraints: str | None = None
    rules_weekly_rhythm: str | None = None
    start_date_start: datetime | None = None
    start_date_end: datetime | None = None
    start_date_is_datetime: bool = False
    end_date_start: datetime | None = None
    end_date_end: datetime | None = None
    end_date_is_datetime: bool = False
    created_time: datetime | None = None
    last_edited_time: datetime | None = None
    archived: bool = False
    url: str | None = None
