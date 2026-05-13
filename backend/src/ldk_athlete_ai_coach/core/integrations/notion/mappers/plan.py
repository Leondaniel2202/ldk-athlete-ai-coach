"""Mapper for translating a NotionPlan Pydantic model into a Plan SQLAlchemy entity."""

from __future__ import annotations

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_plan import NotionPlan
from ldk_athlete_ai_coach.db.models.training import Plan


def map_plan(source: NotionPlan, entity: Plan | None = None) -> Plan:
    """Map a validated :class:`NotionPlan` onto a :class:`Plan` SQLAlchemy entity."""
    if entity is None:
        entity = Plan()

    entity.notion_page_id = source.notion_id
    entity.notion_url = source.url  # type: ignore[assignment]  # enforced by DB constraint
    entity.notion_page_content = source.notion_page_content

    entity.name = source.name
    entity.description = source.description
    entity.start_date = source.start_date
    entity.end_date = source.end_date

    return entity
