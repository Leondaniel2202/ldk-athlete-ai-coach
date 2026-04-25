"""Extractor for Notion Event database entries."""

from __future__ import annotations

from typing import Any

from ldk_athlete_ai_coach.core.integrations.notion.extractors import NotionExtractionError
from ldk_athlete_ai_coach.core.integrations.notion.extractors._helpers import (
    get_date,
    get_first_relation,
    get_page_datetime,
    get_place,
    get_rich_text,
    get_select,
    get_title,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_event import NotionEvent


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

        start_date_start, start_date_end, start_date_is_datetime = get_date(
            props.get("Start date", {})
        )
        end_date_start, end_date_end, end_date_is_datetime = get_date(props.get("End date", {}))
        (
            place_name,
            place_address,
            place_latitude,
            place_longitude,
            place_google_place_id,
        ) = get_place(props.get("Place", {}))

        return NotionEvent(
            notion_id=notion_id,
            name=name,
            event_type=get_select(props.get("Type", {})),
            target=get_rich_text(props.get("Target", {})),
            event_format=get_rich_text(props.get("Format", {})),
            notes=get_rich_text(props.get("Notes", {})),
            priority=get_select(props.get("Priority", {})),
            start_date_start=start_date_start,
            start_date_end=start_date_end,
            start_date_is_datetime=start_date_is_datetime,
            end_date_start=end_date_start,
            end_date_end=end_date_end,
            end_date_is_datetime=end_date_is_datetime,
            place_name=place_name,
            place_address=place_address,
            place_latitude=place_latitude,
            place_longitude=place_longitude,
            place_google_place_id=place_google_place_id,
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
