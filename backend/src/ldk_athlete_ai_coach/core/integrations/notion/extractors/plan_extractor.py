"""Extractor for Notion Plan database entries."""

from __future__ import annotations

from typing import Any

from ldk_athlete_ai_coach.core.integrations.notion.extractors import NotionExtractionError
from ldk_athlete_ai_coach.core.integrations.notion.extractors._helpers import (
    get_date,
    get_page_datetime,
    get_rich_text,
    get_title,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_plan import NotionPlan
from ldk_athlete_ai_coach.utils.date_utils import coerce_to_date


def extract_plan(raw_page: dict[str, Any]) -> NotionPlan:
    """Convert a raw Notion Plan page object into a :class:`NotionPlan` model."""
    try:
        notion_id: str = raw_page["id"]
        props: dict[str, Any] = raw_page["properties"]

        name = get_title(props.get("Name", {}))
        if not name:
            raise NotionExtractionError(
                f"Plan page {notion_id!r} is missing required 'Name' property"
            )

        start_date, _, _ = get_date(props.get("Start date", {}))
        end_date, _, _ = get_date(props.get("End date", {}))
        if start_date is None or end_date is None:
            raise NotionExtractionError(
                f"Plan page {notion_id!r} is missing required start/end date properties"
            )
        start_date_value = coerce_to_date(start_date)
        end_date_value = coerce_to_date(end_date)
        assert start_date_value is not None
        assert end_date_value is not None

        return NotionPlan(
            notion_id=notion_id,
            name=name,
            description=get_rich_text(props.get("Plan goal", {})),
            start_date=start_date_value,
            end_date=end_date_value,
            created_time=get_page_datetime(raw_page, "created_time"),
            last_edited_time=get_page_datetime(raw_page, "last_edited_time"),
            archived=bool(raw_page.get("archived", False)),
            url=raw_page.get("url"),
        )
    except NotionExtractionError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise NotionExtractionError(f"Failed to extract Plan from Notion page: {exc}") from exc
