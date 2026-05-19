"""Factory helpers for building Notion schema objects in tests."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_event import NotionEvent
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_nutrition_guideline import (
    NotionNutritionGuideline,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_phase import NotionPhase
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_plan import NotionPlan
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_session import NotionSession
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_weekly_feedback import (
    NotionWeeklyFeedback,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_workout import NotionWorkout
from ldk_athlete_ai_coach.domain.enums.phase import PhaseType


def make_notion_plan(
    notion_id: str = "plan-1",
    name: str = "Base Plan",
    **kwargs: Any,
) -> NotionPlan:
    """Build a minimal NotionPlan schema for tests."""
    defaults: dict[str, Any] = {
        "notion_id": notion_id,
        "name": name,
        "start_date_start": datetime(2026, 1, 1),
        "end_date_start": datetime(2026, 12, 31),
        "notion_page_content": f"Content for {notion_id}",
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionPlan(**defaults)  # pyright: ignore[reportArgumentType]


def make_notion_phase(
    notion_id: str = "phase-1",
    name: str = "Base Phase",
    **kwargs: Any,
) -> NotionPhase:
    """Build a minimal NotionPhase schema for tests."""
    defaults: dict[str, Any] = {
        "notion_id": notion_id,
        "name": name,
        "phase_type": PhaseType.BASE,
        "focus_tags": ["Run engine"],
        "timeframe_start": datetime(2026, 1, 1),
        "timeframe_end": datetime(2026, 3, 31),
        "notion_page_content": f"Content for {notion_id}",
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionPhase(**defaults)  # pyright: ignore[reportArgumentType]


def make_notion_workout(
    notion_id: str = "workout-1",
    name: str = "Long Run",
    **kwargs: Any,
) -> NotionWorkout:
    """Build a minimal NotionWorkout schema for tests."""
    defaults: dict[str, Any] = {
        "notion_id": notion_id,
        "name": name,
        "notion_page_content": f"Content for {notion_id}",
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionWorkout(**defaults)  # pyright: ignore[reportArgumentType]


def make_notion_nutrition_guideline(
    notion_id: str = "nutrition-1",
    name: str = "Performance Fueling",
    **kwargs: Any,
) -> NotionNutritionGuideline:
    """Build a minimal NotionNutritionGuideline schema for tests."""
    defaults: dict[str, Any] = {
        "notion_id": notion_id,
        "name": name,
        "notion_page_content": f"Content for {notion_id}",
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionNutritionGuideline(**defaults)  # pyright: ignore[reportArgumentType]


def make_notion_event(
    notion_id: str = "event-1",
    name: str = "Goal Race",
    **kwargs: Any,
) -> NotionEvent:
    """Build a minimal NotionEvent schema for tests."""
    defaults: dict[str, Any] = {
        "notion_id": notion_id,
        "name": name,
        "notion_page_content": f"Content for {notion_id}",
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionEvent(**defaults)  # pyright: ignore[reportArgumentType]


def make_notion_session(
    notion_id: str = "session-1",
    name: str = "Morning Run",
    **kwargs: Any,
) -> NotionSession:
    """Build a minimal NotionSession schema for tests."""
    defaults: dict[str, Any] = {
        "notion_id": notion_id,
        "name": name,
        "notion_page_content": f"Content for {notion_id}",
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionSession(**defaults)  # pyright: ignore[reportArgumentType]


def make_notion_weekly_feedback(
    notion_id: str = "feedback-1",
    week: str = "2024-W10",
    **kwargs: Any,
) -> NotionWeeklyFeedback:
    """Build a minimal NotionWeeklyFeedback schema for tests."""
    defaults: dict[str, Any] = {
        "notion_id": notion_id,
        "name": week,
        "week": week,
        "notion_page_content": f"Content for {notion_id}",
        "url": f"https://notion.so/{notion_id}",
    }
    defaults.update(kwargs)
    return NotionWeeklyFeedback(**defaults)  # pyright: ignore[reportArgumentType]


def make_raw_notion_page(
    notion_id: str,
    name_prop: str = "Name",
    name_value: str = "Test Page",
    *,
    archived: bool = False,
) -> dict[str, Any]:
    """Build a minimal raw Notion page dict (as returned by the API)."""
    return {
        "id": notion_id,
        "url": f"https://notion.so/{notion_id}",
        "archived": archived,
        "created_time": "2024-03-01T08:00:00.000Z",
        "last_edited_time": "2024-03-01T08:00:00.000Z",
        "properties": {
            name_prop: {
                "type": "title",
                "title": [{"plain_text": name_value}],
            },
        },
    }
