"""Mapper for translating a NotionEvent Pydantic model into an Event SQLAlchemy entity."""

from __future__ import annotations

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_event import NotionEvent
from ldk_athlete_ai_coach.db.models.training import Event
from ldk_athlete_ai_coach.domain.enums.event import EventPriority, EventStatus, EventType
from ldk_athlete_ai_coach.domain.enums.workout import WorkoutCategory


def normalize_event_type(value: str | None) -> EventType:
    """Normalize a source event type into the domain enum."""
    if value is None:
        return EventType.OTHER

    normalized = value.strip().lower()
    event_types = {
        "race": EventType.RACE,
        "competition": EventType.COMPETITION,
        "benchmark": EventType.BENCHMARK,
        "training event": EventType.TRAINING_EVENT,
        "training": EventType.TRAINING_EVENT,
        "other": EventType.OTHER,
    }
    return event_types.get(normalized, EventType.OTHER)


def normalize_event_priority(value: str | None) -> EventPriority:
    """Normalize a source priority into the domain enum."""
    if value is None:
        return EventPriority.SECONDARY

    normalized = value.strip().lower()
    priorities = {
        "a": EventPriority.PRIMARY,
        "primary": EventPriority.PRIMARY,
        "b": EventPriority.SECONDARY,
        "secondary": EventPriority.SECONDARY,
        "tune-up": EventPriority.TUNE_UP,
        "tune up": EventPriority.TUNE_UP,
        "tuneup": EventPriority.TUNE_UP,
        "c": EventPriority.LOW,
        "low": EventPriority.LOW,
    }
    return priorities.get(normalized, EventPriority.SECONDARY)


def infer_event_sport(
    *,
    name: str,
    event_type: EventType,
) -> WorkoutCategory:
    """Infer the closest current workout category for an event."""
    searchable = " ".join(part for part in (name, event_type.value) if part).lower()

    if "hyrox" in searchable:
        return WorkoutCategory.HYROX
    if "spartan" in searchable or "obstacle" in searchable:
        return WorkoutCategory.CONDITIONING
    if any(token in searchable for token in ("marathon", "half marathon", "10k", "run")):
        return WorkoutCategory.RUN
    return WorkoutCategory.CROSS_TRAINING


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
    entity.event_type = normalize_event_type(source.event_type)
    entity.sport = infer_event_sport(
        name=source.name,
        event_type=entity.event_type,
    )
    entity.priority = normalize_event_priority(source.priority)
    entity.target_time_seconds = None
    entity.target_distance_km = None
    entity.start_at = source.start_date_start
    entity.end_at = source.end_date_start or source.start_date_end or source.end_date_end
    entity.location = source.place_name or source.place_address
    entity.notes = source.notes
    entity.status = EventStatus.PLANNED
    entity.plan_id = plan_id
    entity.race_workout_id = race_workout_id

    return entity
