"""Extracted Notion schema for a Nutrition Guideline page."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class NotionNutritionGuideline(BaseModel):
    """Typed representation of a raw Notion Nutrition Guidelines database entry.

    Fields map to the columns defined in
    :class:`~ldk_athlete_ai_coach.db.models.sport_manager.NutritionGuideline`.
    """

    notion_id: str
    name: str
    goal: str | None = None
    applies_to: list[str] = Field(default_factory=list)
    carb_strategy: str | None = None
    protein_target_g_per_kg: str | None = None
    fat_target_g_per_kg: str | None = None
    hydration_electrolytes: str | None = None
    supplements: str | None = None
    timing_rules: str | None = None
    created_time: datetime | None = None
    last_edited_time: datetime | None = None
    archived: bool = False
    url: str | None = None
