"""Extractor for Notion Nutrition Guideline database entries."""

from __future__ import annotations

from typing import Any

from ldk_athlete_ai_coach.core.integrations.notion.extractors import NotionExtractionError
from ldk_athlete_ai_coach.core.integrations.notion.extractors._helpers import (
    get_multi_select,
    get_page_datetime,
    get_rich_text,
    get_select,
    get_title,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_nutrition_guideline import (
    NotionNutritionGuideline,
)


def extract_nutrition_guideline(raw_page: dict[str, Any]) -> NotionNutritionGuideline:
    """Convert a raw Notion Nutrition Guideline page into a typed schema."""

    try:
        notion_id: str = raw_page["id"]
        props: dict[str, Any] = raw_page["properties"]

        name = get_title(props.get("Name", {}))
        if not name:
            raise NotionExtractionError(
                f"Nutrition Guideline page {notion_id!r} is missing required 'Name' property"
            )

        return NotionNutritionGuideline(
            notion_id=notion_id,
            name=name,
            goal=get_select(props.get("Goal", {})),
            applies_to=get_multi_select(props.get("Applies to", {})),
            carb_strategy=get_rich_text(props.get("Carb strategy", {})),
            protein_target_g_per_kg=get_rich_text(props.get("Protein target (g/kg)", {})),
            fat_target_g_per_kg=get_rich_text(props.get("Fat target (g/kg)", {})),
            hydration_electrolytes=get_rich_text(props.get("Hydration / electrolytes", {})),
            supplements=get_rich_text(props.get("Supplements", {})),
            timing_rules=get_rich_text(props.get("Timing rules", {})),
            created_time=get_page_datetime(raw_page, "created_time"),
            last_edited_time=get_page_datetime(raw_page, "last_edited_time"),
            archived=bool(raw_page.get("archived", False)),
            url=raw_page.get("url"),
        )
    except NotionExtractionError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise NotionExtractionError(
            f"Failed to extract NutritionGuideline from Notion page: {exc}"
        ) from exc
