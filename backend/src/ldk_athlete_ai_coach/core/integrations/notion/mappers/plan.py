"""Mapper for translating a NotionPlan Pydantic model into a Plan SQLAlchemy entity."""

from __future__ import annotations

from datetime import date, datetime

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_plan import NotionPlan
from ldk_athlete_ai_coach.db.models.training import Plan


def require_date(value: datetime | None, *, field_name: str) -> date:
    """Return a date from a required Notion datetime value."""
    if value is None:
        raise ValueError(f"Plan is missing required {field_name}")
    return value.date()


def map_plan(source: NotionPlan, entity: Plan | None = None) -> Plan:
    """Map a validated :class:`NotionPlan` onto a :class:`Plan` SQLAlchemy entity."""
    if entity is None:
        entity = Plan()

    entity.notion_page_id = source.notion_id
    entity.notion_url = source.url  # type: ignore[assignment]  # enforced by DB constraint
    entity.notion_page_content = source.notion_page_content

    entity.name = source.name
    entity.description = source.plan_goal
    entity.start_date = require_date(source.start_date_start, field_name="start_date")
    end_value = source.end_date_start or source.start_date_end or source.end_date_end
    entity.end_date = require_date(end_value, field_name="end_date")

    return entity
