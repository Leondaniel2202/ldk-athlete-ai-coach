"""Mapper for translating a NotionNutritionGuideline model into a NutritionGuideline entity."""

from __future__ import annotations

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_nutrition_guideline import (
    NotionNutritionGuideline,
)
from ldk_athlete_ai_coach.db.models.sport_manager import NutritionGuideline


def map_nutrition_guideline(
    source: NotionNutritionGuideline,
    entity: NutritionGuideline | None = None,
) -> NutritionGuideline:
    """Map a validated :class:`NotionNutritionGuideline` onto a
    :class:`NutritionGuideline` SQLAlchemy entity.

    Args:
        source: Validated Pydantic model extracted from the Notion Nutrition Guidelines database.
        entity: An existing :class:`NutritionGuideline` instance to update in place.
            If ``None`` a new instance is created.

    Returns:
        The populated (new or updated) :class:`NutritionGuideline` entity.
    """
    if entity is None:
        entity = NutritionGuideline()

    # --- identifier fields (NotionSyncMixin) ---------------------------------
    entity.notion_page_id = source.notion_id
    entity.notion_url = source.url  # type: ignore[assignment]  # enforced by DB constraint

    # --- direct 1:1 field mappings -------------------------------------------
    entity.name = source.name
    entity.goal = source.goal
    entity.applies_to = list(source.applies_to)
    entity.carb_strategy = source.carb_strategy
    entity.protein_target_g_per_kg = source.protein_target_g_per_kg
    entity.fat_target_g_per_kg = source.fat_target_g_per_kg
    entity.hydration_electrolytes = source.hydration_electrolytes
    entity.supplements = source.supplements
    entity.timing_rules = source.timing_rules

    return entity
