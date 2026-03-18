"""Extracted Notion schema for a Weekly Feedback page."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class NotionWeeklyFeedback(BaseModel):
    """Typed representation of a raw Notion Feedback database entry.

    Fields map to the columns defined in
    :class:`~ldk_athlete_ai_coach.db.models.sport_manager.Feedback`.
    """

    notion_id: str
    week: str
    energy: float | None = None
    leg_freshness: float | None = None
    motivation: float | None = None
    recovery: float | None = None
    biggest_limitation: str | None = None
    phase_notion_id: str | None = None
    created_time: datetime | None = None
    last_edited_time: datetime | None = None
    archived: bool = False
    url: str | None = None
