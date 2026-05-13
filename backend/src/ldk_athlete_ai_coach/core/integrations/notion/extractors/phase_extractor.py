"""Extractor for Notion Phase database entries."""

from __future__ import annotations

from typing import Any

from ldk_athlete_ai_coach.core.integrations.notion.extractors import NotionExtractionError
from ldk_athlete_ai_coach.core.integrations.notion.extractors._helpers import (
    get_date,
    get_first_relation,
    get_multi_select,
    get_page_datetime,
    get_property_by_alias,
    get_rich_text,
    get_select,
    get_title,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_phase import NotionPhase
from ldk_athlete_ai_coach.domain.enums.phase import PhaseFocusTag, PhaseType
from ldk_athlete_ai_coach.utils.date_utils import coerce_to_date


def extract_phase(raw_page: dict[str, Any]) -> NotionPhase:
    """Convert a raw Notion Phase page object into a :class:`NotionPhase` model.

    Args:
        raw_page: A single entry from the Notion Phases database as returned by
            :meth:`~ldk_athlete_ai_coach.core.integrations.notion.client.NotionClient.iter_database_entries`.

    Returns:
        A validated :class:`NotionPhase` instance.

    Raises:
        NotionExtractionError: If required fields are missing or the payload is malformed.

    """
    try:
        notion_id: str = raw_page["id"]
        props: dict[str, Any] = raw_page["properties"]

        name = get_title(props.get("Name", {}))
        if not name:
            raise NotionExtractionError(
                f"Phase page {notion_id!r} is missing required 'Name' property"
            )

        start_date, end_date, _ = get_date(props.get("Timeframe", {}))
        if start_date is None or end_date is None:
            raise NotionExtractionError(
                f"Phase page {notion_id!r} is missing required 'Timeframe' property"
            )
        start_date_value = coerce_to_date(start_date)
        end_date_value = coerce_to_date(end_date)
        assert start_date_value is not None
        assert end_date_value is not None
        phase_type_prop = get_property_by_alias(props, "Phase type", "Phase Type")
        phase_type = PhaseType(get_select(phase_type_prop) or PhaseType.UNKNOWN)
        focus_tags_prop = get_property_by_alias(props, "Focus tags", "Focus Tags")
        nutrition_guideline_prop = get_property_by_alias(
            props, "Nutrition Guidelines", "Nutrition Guideline"
        )

        return NotionPhase(
            notion_id=notion_id,
            name=name,
            notes=get_rich_text(props.get("Notes", {})),
            phase_type=phase_type,
            focus_tags=[PhaseFocusTag(value) for value in get_multi_select(focus_tags_prop)],
            start_date=start_date_value,
            end_date=end_date_value,
            plan_notion_id=get_first_relation(props.get("Plan", {})),
            nutrition_guideline_notion_id=get_first_relation(nutrition_guideline_prop),
            created_time=get_page_datetime(raw_page, "created_time"),
            last_edited_time=get_page_datetime(raw_page, "last_edited_time"),
            archived=bool(raw_page.get("archived", False)),
            url=raw_page.get("url"),
        )
    except NotionExtractionError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise NotionExtractionError(f"Failed to extract Phase from Notion page: {exc}") from exc
