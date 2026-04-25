"""Extracted Notion schema for a Weekly Feedback page."""

from __future__ import annotations

from datetime import datetime

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_base import NotionBaseSchema


class NotionWeeklyFeedback(NotionBaseSchema):
    """Typed representation of a raw Notion Feedback database entry.

    Inherits common Notion identity fields from :class:`NotionBaseSchema`.
    ``name`` mirrors ``week`` to provide a common title field across schemas.
    The remaining fields map to the columns defined in
    :class:`~ldk_athlete_ai_coach.db.models.training.WeeklyFeedback`.
    """

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
