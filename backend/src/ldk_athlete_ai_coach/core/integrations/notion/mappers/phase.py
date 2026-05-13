"""Mapper for translating a NotionPhase Pydantic model into a Phase SQLAlchemy entity."""

from __future__ import annotations

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_phase import NotionPhase
from ldk_athlete_ai_coach.db.models.training import Phase


def map_phase(
    source: NotionPhase,
    entity: Phase | None = None,
    *,
    plan_id: int | None = None,
    nutrition_guideline_id: int | None = None,
) -> Phase:
    """Map a validated :class:`NotionPhase` onto a :class:`Phase` SQLAlchemy entity.

    Args:
        source: Validated Pydantic model extracted from the Notion Phases database.
        entity: An existing :class:`Phase` instance to update in place.
            If ``None`` a new instance is created.
        plan_id: Resolved local primary key of the related :class:`Plan` row.
            Pass ``None`` when the relation is not yet resolved.
        nutrition_guideline_id: Resolved local primary key of the related
            :class:`NutritionGuideline` row.  Pass ``None`` when the relation
            is not yet resolved.

    Returns:
        The populated (new or updated) :class:`Phase` entity.

    """
    if entity is None:
        entity = Phase()

    # --- identifier fields (NotionSyncMixin) ---------------------------------
    entity.notion_page_id = source.notion_id
    entity.notion_url = source.url  # type: ignore[assignment]  # enforced by DB constraint
    entity.notion_page_content = source.notion_page_content

    # --- direct 1:1 field mappings -------------------------------------------
    entity.name = source.name
    entity.notes = source.notes
    entity.phase_type = source.phase_type
    entity.focus_tags = list(source.focus_tags)
    entity.start_date = source.start_date
    entity.end_date = source.end_date

    # --- scalar foreign key fields -------------------------------------------
    # Callers that have already resolved Notion page IDs to local DB IDs should
    # pass the resolved values; otherwise both fields are set to None.
    entity.plan_id = plan_id
    entity.nutrition_guideline_id = nutrition_guideline_id

    return entity
