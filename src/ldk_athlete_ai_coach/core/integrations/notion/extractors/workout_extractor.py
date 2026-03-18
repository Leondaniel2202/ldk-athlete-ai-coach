"""Extractor for Notion Workout database entries."""

from __future__ import annotations

from typing import Any

from ldk_athlete_ai_coach.core.integrations.notion.extractors import NotionExtractionError
from ldk_athlete_ai_coach.core.integrations.notion.extractors._helpers import (
    get_checkbox,
    get_date,
    get_first_relation,
    get_multi_select,
    get_number,
    get_page_datetime,
    get_rich_text,
    get_select,
    get_title,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_workout import NotionWorkout


def extract_workout(raw_page: dict[str, Any]) -> NotionWorkout:
    """Convert a raw Notion Workout page object into a :class:`NotionWorkout` model.

    Args:
        raw_page: A single entry from the Notion Workouts database as returned by
            :meth:`~ldk_athlete_ai_coach.core.integrations.notion.client.NotionClient.iter_database_entries`.

    Returns:
        A validated :class:`NotionWorkout` instance.

    Raises:
        NotionExtractionError: If required fields are missing or the payload is malformed.
    """
    try:
        notion_id: str = raw_page["id"]
        props: dict[str, Any] = raw_page["properties"]

        name = get_title(props.get("Name", {}))
        if not name:
            raise NotionExtractionError(
                f"Workout page {notion_id!r} is missing required 'Name' property"
            )

        date_start, date_end, date_is_datetime = get_date(props.get("Date", {}))

        return NotionWorkout(
            notion_id=notion_id,
            name=name,
            date_start=date_start,
            date_end=date_end,
            date_is_datetime=date_is_datetime,
            category=get_select(props.get("Category", {})),
            difficulty=get_select(props.get("Difficulty", {})),
            equipment=get_multi_select(props.get("Equipment", {})),
            impact=get_select(props.get("Impact", {})),
            metrics_to_record=get_multi_select(props.get("Metrics to Record", {})),
            purpose=get_multi_select(props.get("Purpose", {})),
            primarily_used_muscle_group=get_multi_select(
                props.get("Primarily Used Muscle Group", {})
            ),
            planned_distance_km=get_number(props.get("Planned Distance (km)", {})),
            planned_duration_min=get_number(props.get("Planned Duration (min)", {})),
            planned_rpe=get_number(props.get("Planned RPE", {})),
            planned_week_number=get_number(props.get("Planned Week Number", {})),
            actual_rpe=get_number(props.get("Actual RPE", {})),
            additional_info=get_rich_text(props.get("Additional Info", {})),
            cancelled=get_checkbox(props.get("Cancelled", {})),
            skipped=get_checkbox(props.get("Skipped", {})),
            phase_notion_id=get_first_relation(props.get("Phase", {})),
            created_time=get_page_datetime(raw_page, "created_time"),
            last_edited_time=get_page_datetime(raw_page, "last_edited_time"),
            archived=bool(raw_page.get("archived", False)),
            url=raw_page.get("url"),
        )
    except NotionExtractionError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise NotionExtractionError(f"Failed to extract Workout from Notion page: {exc}") from exc
