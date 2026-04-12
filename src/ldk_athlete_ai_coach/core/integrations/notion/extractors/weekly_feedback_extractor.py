"""Extractor for Notion Weekly Feedback database entries."""

from __future__ import annotations

from typing import Any

from ldk_athlete_ai_coach.core.integrations.notion.extractors import NotionExtractionError
from ldk_athlete_ai_coach.core.integrations.notion.extractors._helpers import (
    get_first_relation,
    get_number,
    get_page_datetime,
    get_select,
    get_title,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_weekly_feedback import (
    NotionWeeklyFeedback,
)


def extract_weekly_feedback(raw_page: dict[str, Any]) -> NotionWeeklyFeedback:
    """Convert a raw Notion Feedback page object into a :class:`NotionWeeklyFeedback` model.

    Args:
        raw_page: A single entry from the Notion Feedback database as returned by
            :meth:`~ldk_athlete_ai_coach.core.integrations.notion.client.NotionClient.iter_database_entries`.

    Returns:
        A validated :class:`NotionWeeklyFeedback` instance.

    Raises:
        NotionExtractionError: If required fields are missing or the payload is malformed.

    """
    try:
        notion_id: str = raw_page["id"]
        props: dict[str, Any] = raw_page["properties"]

        week = get_title(props.get("Week", {}))
        if not week:
            raise NotionExtractionError(
                f"Feedback page {notion_id!r} is missing required 'Week' property"
            )

        return NotionWeeklyFeedback(
            notion_id=notion_id,
            name=week,
            week=week,
            energy=get_number(props.get("Energy", {})),
            leg_freshness=get_number(props.get("Leg Freshness", {})),
            motivation=get_number(props.get("Motivation", {})),
            recovery=get_number(props.get("Recovery", {})),
            biggest_limitation=get_select(props.get("Biggest Limitation", {})),
            phase_notion_id=get_first_relation(props.get("Phase", {})),
            created_time=get_page_datetime(raw_page, "created_time"),
            last_edited_time=get_page_datetime(raw_page, "last_edited_time"),
            archived=bool(raw_page.get("archived", False)),
            url=raw_page.get("url"),
        )
    except NotionExtractionError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise NotionExtractionError(
            f"Failed to extract WeeklyFeedback from Notion page: {exc}"
        ) from exc
