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

        start_date_start, start_date_end, start_date_is_datetime = get_date(
            props.get("Start date", {})
        )
        end_date_start, end_date_end, end_date_is_datetime = get_date(props.get("End date", {}))

        return NotionPlan(
            notion_id=notion_id,
            name=name,
            plan_goal=get_rich_text(props.get("Plan goal", {})),
            constraints=get_rich_text(props.get("Constraints", {})),
            rules_weekly_rhythm=get_rich_text(props.get("Rules / weekly rhythm", {})),
            start_date_start=start_date_start,
            start_date_end=start_date_end,
            start_date_is_datetime=start_date_is_datetime,
            end_date_start=end_date_start,
            end_date_end=end_date_end,
            end_date_is_datetime=end_date_is_datetime,
            created_time=get_page_datetime(raw_page, "created_time"),
            last_edited_time=get_page_datetime(raw_page, "last_edited_time"),
            archived=bool(raw_page.get("archived", False)),
            url=raw_page.get("url"),
        )
    except NotionExtractionError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise NotionExtractionError(f"Failed to extract Plan from Notion page: {exc}") from exc
