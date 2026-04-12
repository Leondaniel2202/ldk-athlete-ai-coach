"""Extractor for Notion Tracked Session database entries."""

from __future__ import annotations

from typing import Any

from ldk_athlete_ai_coach.core.integrations.notion.extractors import NotionExtractionError
from ldk_athlete_ai_coach.core.integrations.notion.extractors._helpers import (
    get_date,
    get_first_relation,
    get_number,
    get_page_datetime,
    get_rich_text,
    get_select,
    get_title,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_session import NotionSession


def extract_session(raw_page: dict[str, Any]) -> NotionSession:
    """Convert a raw Notion Tracked Session page object into a :class:`NotionSession` model.

    Args:
        raw_page: A single entry from the Notion Tracked Sessions database as returned by
            :meth:`~ldk_athlete_ai_coach.core.integrations.notion.client.NotionClient.iter_database_entries`.

    Returns:
        A validated :class:`NotionSession` instance.

    Raises:
        NotionExtractionError: If required fields are missing or the payload is malformed.

    """
    try:
        notion_id: str = raw_page["id"]
        props: dict[str, Any] = raw_page["properties"]

        name = get_title(props.get("Name", {}))
        if not name:
            raise NotionExtractionError(
                f"Session page {notion_id!r} is missing required 'Name' property"
            )

        start_start, start_end, start_is_datetime = get_date(props.get("Start", {}))
        end_start, end_end, end_is_datetime = get_date(props.get("End", {}))

        return NotionSession(
            notion_id=notion_id,
            name=name,
            source=get_select(props.get("Source", {})),
            session_type=get_select(props.get("Session Type", {})),
            external_id=get_rich_text(props.get("External ID", {})),
            start_start=start_start,
            start_end=start_end,
            start_is_datetime=start_is_datetime,
            end_start=end_start,
            end_end=end_end,
            end_is_datetime=end_is_datetime,
            active_energy_kj=get_number(props.get("Active Energy (kJ)", {})),
            active_energy_burned_kj=get_number(props.get("Active Energy Burned (kJ)", {})),
            avg_hr=get_number(props.get("Avg HR", {})),
            max_hr=get_number(props.get("Max HR", {})),
            calories_kcal=get_number(props.get("Calories (kcal)", {})),
            distance_km=get_number(props.get("Distance (km)", {})),
            duration_min=get_number(props.get("Duration (min)", {})),
            elevation_ascended_m=get_number(props.get("Elevation Ascended (m)", {})),
            elevation_descended_m=get_number(props.get("Elevation Descended (m)", {})),
            intensity_kcal_per_hr_kg=get_number(props.get("Intensity (kcal/hr/kg)", {})),
            step_cadence_count_per_min=get_number(props.get("Step Cadence (count/min)", {})),
            steps=get_number(props.get("Steps", {})),
            workout_notion_id=get_first_relation(props.get("Workout", {})),
            created_time=get_page_datetime(raw_page, "created_time"),
            last_edited_time=get_page_datetime(raw_page, "last_edited_time"),
            archived=bool(raw_page.get("archived", False)),
            url=raw_page.get("url"),
        )
    except NotionExtractionError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise NotionExtractionError(f"Failed to extract Session from Notion page: {exc}") from exc
