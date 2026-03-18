"""Mapper for translating a NotionWeeklyFeedback Pydantic model into a Feedback entity."""

from __future__ import annotations

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_weekly_feedback import (
    NotionWeeklyFeedback,
)
from ldk_athlete_ai_coach.db.models.sport_manager import Feedback


def map_feedback(
    source: NotionWeeklyFeedback,
    entity: Feedback | None = None,
    *,
    phase_id: int | None = None,
) -> Feedback:
    """Map a validated :class:`NotionWeeklyFeedback` onto a :class:`Feedback` SQLAlchemy entity.

    Args:
        source: Validated Pydantic model extracted from the Notion Feedback database.
        entity: An existing :class:`Feedback` instance to update in place.
            If ``None`` a new instance is created.
        phase_id: Resolved local primary key of the related :class:`Phase` row.
            Pass ``None`` when the relation is not yet resolved.

    Returns:
        The populated (new or updated) :class:`Feedback` entity.
    """
    if entity is None:
        entity = Feedback()

    # --- identifier fields (NotionSyncMixin) ---------------------------------
    entity.notion_page_id = source.notion_id
    entity.notion_url = source.url  # type: ignore[assignment]  # enforced by DB constraint

    # --- direct 1:1 field mappings -------------------------------------------
    entity.week = source.week
    entity.energy = source.energy
    entity.leg_freshness = source.leg_freshness
    entity.motivation = source.motivation
    entity.recovery = source.recovery
    entity.biggest_limitation = source.biggest_limitation

    # --- scalar foreign key fields -------------------------------------------
    # Callers that have already resolved the Notion phase page ID to a local DB
    # ID should pass the resolved value; otherwise the field is set to None.
    entity.phase_id = phase_id

    return entity
