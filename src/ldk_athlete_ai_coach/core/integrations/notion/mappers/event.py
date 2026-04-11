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

    entity.name = source.name
    entity.event_type = source.event_type
    entity.target = source.target
    entity.event_format = source.event_format
    entity.notes = source.notes
    entity.priority = source.priority
    entity.start_date_start = source.start_date_start
    entity.start_date_end = source.start_date_end
    entity.start_date_is_datetime = source.start_date_is_datetime
    entity.end_date_start = source.end_date_start
    entity.end_date_end = source.end_date_end
    entity.end_date_is_datetime = source.end_date_is_datetime
    entity.place_name = source.place_name
    entity.place_address = source.place_address
    entity.place_latitude = source.place_latitude
    entity.place_longitude = source.place_longitude
    entity.place_google_place_id = source.place_google_place_id
    entity.plan_id = plan_id
    entity.race_workout_id = race_workout_id

    return entity
