"""Extractor for Notion Event database entries."""

from __future__ import annotations

from typing import Any

from ldk_athlete_ai_coach.core.integrations.notion.extractors import NotionExtractionError
from ldk_athlete_ai_coach.core.integrations.notion.extractors._helpers import (
    get_date,
    get_first_relation,
    get_number,
    get_page_datetime,
    get_place,
    get_property_by_alias,
    get_rich_text,
    get_select,
    get_title,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_event import NotionEvent
from ldk_athlete_ai_coach.domain.enums.event import (
    EventPlanRole,
    EventPriority,
    EventStatus,
    EventType,
)
from ldk_athlete_ai_coach.domain.enums.workout import WorkoutCategory


def extract_event(raw_page: dict[str, Any]) -> NotionEvent:
    """Convert a raw Notion Event page object into a :class:`NotionEvent` model."""
    try:
        notion_id: str = raw_page["id"]
        props: dict[str, Any] = raw_page["properties"]

        name = get_title(props.get("Name", {}))
        if not name:
            raise NotionExtractionError(
                f"Event page {notion_id!r} is missing required 'Name' property"
            )

        start_at, _, _ = get_date(props.get("Start date", {}))
        end_at, _, _ = get_date(props.get("End date", {}))
        (
            place_name,
            place_address,
            _place_latitude,
            _place_longitude,
            _place_google_place_id,
        ) = get_place(props.get("Place", {}))

        return NotionEvent(
            notion_id=notion_id,
            name=name,
            event_type=EventType(get_select(props.get("Type", {})) or EventType.UNKNOWN),
            sport=WorkoutCategory(get_select(props.get("Sport", {})) or WorkoutCategory.UNKNOWN),
            priority=EventPriority(get_select(props.get("Priority", {})) or EventPriority.UNKNOWN),
            status=EventStatus(get_select(props.get("Status", {})) or EventStatus.UNKNOWN),
            role_in_plan=(
                EventPlanRole(role_value)
                if (role_value := get_select(get_property_by_alias(props, "Role in plan", "Role")))
                else None
            ),
            target=get_rich_text(props.get("Target", {})),
            event_format=get_rich_text(props.get("Format", {})),
            target_time_seconds=(
                int(target_time)
                if (
                    target_time := get_number(
                        get_property_by_alias(
                            props,
                            "Target time (seconds)",
                            "Target Time (seconds)",
                            "Target time seconds",
                        )
                    )
                )
                is not None
                else None
            ),
            target_distance_km=get_number(
                get_property_by_alias(props, "Target distance (km)", "Target Distance (km)")
            ),
            start_at=start_at,
            end_at=end_at,
            location=place_name or place_address,
            notes=get_rich_text(props.get("Notes", {})),
            plan_notion_id=get_first_relation(props.get("Plan", {})),
            race_workout_notion_id=get_first_relation(props.get("Race Workout", {})),
            created_time=get_page_datetime(raw_page, "created_time"),
            last_edited_time=get_page_datetime(raw_page, "last_edited_time"),
            archived=bool(raw_page.get("archived", False)),
            url=raw_page.get("url"),
        )
    except NotionExtractionError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise NotionExtractionError(f"Failed to extract Event from Notion page: {exc}") from exc
