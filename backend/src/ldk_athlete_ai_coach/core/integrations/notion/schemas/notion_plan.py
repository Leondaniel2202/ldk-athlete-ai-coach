"""Extracted Notion schema for a Plan page."""

from __future__ import annotations

from datetime import date, datetime

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_base import NotionBaseSchema


class NotionPlan(NotionBaseSchema):
    """Typed representation of a raw Notion Plan database entry."""

    description: str | None = None
    start_date: date
    end_date: date
    created_time: datetime | None = None
    last_edited_time: datetime | None = None
    archived: bool = False
    url: str | None = None
