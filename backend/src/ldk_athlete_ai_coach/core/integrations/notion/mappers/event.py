"""Mapper for translating a NotionEvent Pydantic model into an Event SQLAlchemy entity."""

from __future__ import annotations

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_event import NotionEvent
from ldk_athlete_ai_coach.db.models.training import Event


def map_event(
    source: NotionEvent,
    entity: Event | None = None,
    *,
    plan_id: int | None = None,
    race_workout_id: int | None = None,
) -> Event:
    """Map a validated :class:`NotionEvent` onto an :class:`Event` SQLAlchemy entity."""
    if entity is None:
        entity = Event()

    entity.notion_page_id = source.notion_id
    entity.notion_url = source.url  # type: ignore[assignment]  # enforced by DB constraint
    entity.notion_page_content = source.notion_page_content

    entity.name = source.name
    entity.event_type = source.event_type
    entity.sport = source.sport
    entity.priority = source.priority
    entity.status = source.status
    entity.role_in_plan = source.role_in_plan
    entity.target = source.target
    entity.event_format = source.event_format
    entity.target_time_seconds = source.target_time_seconds
    entity.target_distance_km = source.target_distance_km
    entity.start_at = source.start_at
    entity.end_at = source.end_at
    entity.location = source.location
    entity.notes = source.notes
    entity.plan_id = plan_id
    entity.race_workout_id = race_workout_id

    return entity
