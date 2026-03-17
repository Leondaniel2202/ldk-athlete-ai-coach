"""Extracted Notion schema for a Phase page."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class NotionPhase(BaseModel):
    """Typed representation of a raw Notion Phase database entry.

    Fields map to the columns defined in
    :class:`~ldk_athlete_ai_coach.db.models.sport_manager.Phase`.
    Relation fields store the Notion page ID of the related entry so that the
    mapping layer can resolve them later without touching the Notion API again.
    """

    notion_id: str
    name: str
    notes: str | None = None
    phase_type: str | None = None
    focus_tags: list[str] = Field(default_factory=list)
    weekly_structure: str | None = None
    timeframe_start: datetime | None = None
    timeframe_end: datetime | None = None
    timeframe_is_datetime: bool = False
    plan_notion_id: str | None = None
    nutrition_guideline_notion_id: str | None = None
    created_time: datetime | None = None
    last_edited_time: datetime | None = None
    archived: bool = False
    url: str | None = None
