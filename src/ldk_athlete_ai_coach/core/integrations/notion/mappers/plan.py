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
    entity.plan_goal = source.plan_goal
    entity.constraints = source.constraints
    entity.rules_weekly_rhythm = source.rules_weekly_rhythm
    entity.start_date_start = source.start_date_start
    entity.start_date_end = source.start_date_end
    entity.start_date_is_datetime = source.start_date_is_datetime
    entity.end_date_start = source.end_date_start
    entity.end_date_end = source.end_date_end
    entity.end_date_is_datetime = source.end_date_is_datetime

    return entity
