"""Extracted Notion schema for a Tracked Session page."""

from __future__ import annotations

from datetime import datetime

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_base import NotionBaseSchema
from ldk_athlete_ai_coach.domain.enums.session import SessionSource, SessionType


class NotionSession(NotionBaseSchema):
    """Typed representation of a raw Notion Tracked Session database entry.

    Inherits common Notion identity fields from :class:`NotionBaseSchema`.
    The remaining fields map to the columns defined in
    :class:`~ldk_athlete_ai_coach.db.models.training.TrackedSession`.
    """

    source: SessionSource
    session_type: SessionType
    external_id: str | None = None
    start_at: datetime
    end_at: datetime | None = None
    actual_rpe: float | None = None
    active_energy_kj: float | None = None
    active_energy_burned_kj: float | None = None
    avg_hr: float | None = None
    max_hr: float | None = None
    calories_kcal: float | None = None
    distance_km: float | None = None
    duration_min: float | None = None
    elevation_ascended_m: float | None = None
    elevation_descended_m: float | None = None
    intensity_kcal_per_hr_kg: float | None = None
    step_cadence_count_per_min: float | None = None
    steps: float | None = None
    workout_notion_id: str | None = None
    created_time: datetime | None = None
    last_edited_time: datetime | None = None
    archived: bool = False
    url: str | None = None
