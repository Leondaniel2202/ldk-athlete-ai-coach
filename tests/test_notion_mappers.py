"""Unit tests for the Notion mapper layer."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ldk_athlete_ai_coach.core.integrations.notion.mappers.feedback import map_feedback
from ldk_athlete_ai_coach.core.integrations.notion.mappers.nutrition import (
    map_nutrition_guideline,
)
from ldk_athlete_ai_coach.core.integrations.notion.mappers.phase import map_phase
from ldk_athlete_ai_coach.core.integrations.notion.mappers.workout import map_workout
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_nutrition_guideline import (
    NotionNutritionGuideline,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_phase import NotionPhase
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_weekly_feedback import (
    NotionWeeklyFeedback,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_workout import NotionWorkout
from ldk_athlete_ai_coach.db.models.sport_manager import (
    Feedback,
    NutritionGuideline,
    Phase,
    Workout,
)

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_DT = datetime(2024, 3, 1, 8, 0, 0, tzinfo=UTC)
_DT2 = datetime(2024, 6, 30, 20, 0, 0, tzinfo=UTC)


# ===========================================================================
# Phase mapper
# ===========================================================================


def _make_notion_phase(**overrides: object) -> NotionPhase:
    defaults: dict[str, object] = {
        "notion_id": "phase-abc",
        "name": "Base Phase",
        "notes": "Focus on aerobic base",
        "phase_type": "Base",
        "focus_tags": ["Endurance", "Aerobic"],
        "weekly_structure": "Mon: Run, Wed: Bike",
        "timeframe_start": _DT,
        "timeframe_end": _DT2,
        "timeframe_is_datetime": False,
        "plan_notion_id": "plan-xyz",
        "nutrition_guideline_notion_id": "nutrition-xyz",
        "url": "https://notion.so/phase-abc",
        "archived": False,
    }
    defaults.update(overrides)
    return NotionPhase(**defaults)  # type: ignore[arg-type]


class TestMapPhase:
    def test_create_new_entity(self) -> None:
        source = _make_notion_phase()
        entity = map_phase(source)

        assert isinstance(entity, Phase)
        assert entity.notion_page_id == "phase-abc"
        assert entity.notion_url == "https://notion.so/phase-abc"
        assert entity.name == "Base Phase"
        assert entity.notes == "Focus on aerobic base"
        assert entity.phase_type == "Base"
        assert entity.focus_tags == ["Endurance", "Aerobic"]
        assert entity.weekly_structure == "Mon: Run, Wed: Bike"
        assert entity.timeframe_start == _DT
        assert entity.timeframe_end == _DT2
        assert entity.timeframe_is_datetime is False

    def test_create_new_entity_has_no_fk_ids_by_default(self) -> None:
        source = _make_notion_phase()
        entity = map_phase(source)

        assert entity.plan_id is None
        assert entity.nutrition_guideline_id is None

    def test_scalar_foreign_key_fields_are_assigned(self) -> None:
        source = _make_notion_phase()
        entity = map_phase(source, plan_id=7, nutrition_guideline_id=3)

        assert entity.plan_id == 7
        assert entity.nutrition_guideline_id == 3

    def test_update_existing_entity(self) -> None:
        existing = Phase()
        existing.name = "Old Name"
        existing.notes = "Old notes"

        source = _make_notion_phase(name="Updated Phase", notes="New notes")
        result = map_phase(source, existing)

        assert result is existing
        assert result.name == "Updated Phase"
        assert result.notes == "New notes"

    def test_overwrite_existing_fk_with_new_value(self) -> None:
        existing = Phase()
        existing.plan_id = 99

        source = _make_notion_phase()
        result = map_phase(source, existing, plan_id=42)

        assert result.plan_id == 42

    def test_none_values_are_propagated(self) -> None:
        source = _make_notion_phase(
            notes=None,
            phase_type=None,
            weekly_structure=None,
            timeframe_start=None,
            timeframe_end=None,
            url=None,
        )
        entity = map_phase(source)

        assert entity.notes is None
        assert entity.phase_type is None
        assert entity.weekly_structure is None
        assert entity.timeframe_start is None
        assert entity.timeframe_end is None
        assert entity.notion_url is None

    def test_focus_tags_list_is_copied(self) -> None:
        tags = ["Speed", "Hills"]
        source = _make_notion_phase(focus_tags=tags)
        entity = map_phase(source)

        # Mutating the original list must not affect the entity
        tags.append("Extra")
        assert entity.focus_tags == ["Speed", "Hills"]

    def test_fk_fields_reset_to_none_when_not_passed(self) -> None:
        existing = Phase()
        existing.plan_id = 5
        existing.nutrition_guideline_id = 10

        source = _make_notion_phase()
        result = map_phase(source, existing)

        assert result.plan_id is None
        assert result.nutrition_guideline_id is None


# ===========================================================================
# Workout mapper
# ===========================================================================


def _make_notion_workout(**overrides: object) -> NotionWorkout:
    defaults: dict[str, object] = {
        "notion_id": "workout-abc",
        "name": "Morning Run",
        "date_start": _DT,
        "date_end": _DT2,
        "date_is_datetime": True,
        "category": "Run",
        "difficulty": "Moderate",
        "equipment": ["Shoes"],
        "impact": "Low",
        "metrics_to_record": ["HR", "Pace"],
        "purpose": ["Aerobic"],
        "primarily_used_muscle_group": ["Legs"],
        "planned_distance_km": 10.0,
        "planned_duration_min": 60.0,
        "planned_rpe": 6.0,
        "planned_week_number": 3.0,
        "actual_rpe": 5.5,
        "additional_info": "Easy effort",
        "cancelled": False,
        "skipped": False,
        "phase_notion_id": "phase-xyz",
        "url": "https://notion.so/workout-abc",
        "archived": False,
    }
    defaults.update(overrides)
    return NotionWorkout(**defaults)  # type: ignore[arg-type]


class TestMapWorkout:
    def test_create_new_entity(self) -> None:
        source = _make_notion_workout()
        entity = map_workout(source)

        assert isinstance(entity, Workout)
        assert entity.notion_page_id == "workout-abc"
        assert entity.notion_url == "https://notion.so/workout-abc"
        assert entity.name == "Morning Run"
        assert entity.date_start == _DT
        assert entity.date_end == _DT2
        assert entity.date_is_datetime is True
        assert entity.category == "Run"
        assert entity.difficulty == "Moderate"
        assert entity.equipment == ["Shoes"]
        assert entity.impact == "Low"
        assert entity.metrics_to_record == ["HR", "Pace"]
        assert entity.purpose == ["Aerobic"]
        assert entity.primarily_used_muscle_group == ["Legs"]
        assert entity.planned_distance_km == pytest.approx(10.0)
        assert entity.planned_duration_min == pytest.approx(60.0)
        assert entity.planned_rpe == pytest.approx(6.0)
        assert entity.planned_week_number == pytest.approx(3.0)
        assert entity.actual_rpe == pytest.approx(5.5)
        assert entity.additional_info == "Easy effort"
        assert entity.cancelled is False
        assert entity.skipped is False

    def test_create_new_entity_has_no_phase_id_by_default(self) -> None:
        source = _make_notion_workout()
        entity = map_workout(source)

        assert entity.phase_id is None

    def test_scalar_foreign_key_phase_id_is_assigned(self) -> None:
        source = _make_notion_workout()
        entity = map_workout(source, phase_id=12)

        assert entity.phase_id == 12

    def test_update_existing_entity(self) -> None:
        existing = Workout()
        existing.name = "Old Workout"
        existing.category = "Bike"

        source = _make_notion_workout(name="Updated Workout", category="Run")
        result = map_workout(source, existing)

        assert result is existing
        assert result.name == "Updated Workout"
        assert result.category == "Run"

    def test_overwrite_existing_phase_id(self) -> None:
        existing = Workout()
        existing.phase_id = 99

        source = _make_notion_workout()
        result = map_workout(source, existing, phase_id=7)

        assert result.phase_id == 7

    def test_none_values_are_propagated(self) -> None:
        source = _make_notion_workout(
            date_start=None,
            date_end=None,
            category=None,
            difficulty=None,
            impact=None,
            planned_distance_km=None,
            planned_duration_min=None,
            planned_rpe=None,
            planned_week_number=None,
            actual_rpe=None,
            additional_info=None,
            url=None,
        )
        entity = map_workout(source)

        assert entity.date_start is None
        assert entity.date_end is None
        assert entity.category is None
        assert entity.difficulty is None
        assert entity.impact is None
        assert entity.planned_distance_km is None
        assert entity.planned_duration_min is None
        assert entity.planned_rpe is None
        assert entity.planned_week_number is None
        assert entity.actual_rpe is None
        assert entity.additional_info is None
        assert entity.notion_url is None

    def test_list_fields_are_copied(self) -> None:
        equipment = ["Bike"]
        source = _make_notion_workout(equipment=equipment)
        entity = map_workout(source)

        equipment.append("Helmet")
        assert entity.equipment == ["Bike"]

    def test_fk_field_reset_to_none_when_not_passed(self) -> None:
        existing = Workout()
        existing.phase_id = 5

        source = _make_notion_workout()
        result = map_workout(source, existing)

        assert result.phase_id is None


# ===========================================================================
# Feedback mapper
# ===========================================================================


def _make_notion_feedback(**overrides: object) -> NotionWeeklyFeedback:
    defaults: dict[str, object] = {
        "notion_id": "feedback-abc",
        "week": "2024-W10",
        "energy": 4.0,
        "leg_freshness": 3.5,
        "motivation": 5.0,
        "recovery": 4.5,
        "biggest_limitation": "Time",
        "phase_notion_id": "phase-xyz",
        "url": "https://notion.so/feedback-abc",
        "archived": False,
    }
    defaults.update(overrides)
    return NotionWeeklyFeedback(**defaults)  # type: ignore[arg-type]


class TestMapFeedback:
    def test_create_new_entity(self) -> None:
        source = _make_notion_feedback()
        entity = map_feedback(source)

        assert isinstance(entity, Feedback)
        assert entity.notion_page_id == "feedback-abc"
        assert entity.notion_url == "https://notion.so/feedback-abc"
        assert entity.week == "2024-W10"
        assert entity.energy == pytest.approx(4.0)
        assert entity.leg_freshness == pytest.approx(3.5)
        assert entity.motivation == pytest.approx(5.0)
        assert entity.recovery == pytest.approx(4.5)
        assert entity.biggest_limitation == "Time"

    def test_create_new_entity_has_no_phase_id_by_default(self) -> None:
        source = _make_notion_feedback()
        entity = map_feedback(source)

        assert entity.phase_id is None

    def test_scalar_foreign_key_phase_id_is_assigned(self) -> None:
        source = _make_notion_feedback()
        entity = map_feedback(source, phase_id=8)

        assert entity.phase_id == 8

    def test_update_existing_entity(self) -> None:
        existing = Feedback()
        existing.week = "2024-W01"
        existing.energy = 2.0

        source = _make_notion_feedback(week="2024-W10", energy=4.0)
        result = map_feedback(source, existing)

        assert result is existing
        assert result.week == "2024-W10"
        assert result.energy == pytest.approx(4.0)

    def test_overwrite_existing_phase_id(self) -> None:
        existing = Feedback()
        existing.phase_id = 99

        source = _make_notion_feedback()
        result = map_feedback(source, existing, phase_id=3)

        assert result.phase_id == 3

    def test_none_values_are_propagated(self) -> None:
        source = _make_notion_feedback(
            energy=None,
            leg_freshness=None,
            motivation=None,
            recovery=None,
            biggest_limitation=None,
            url=None,
        )
        entity = map_feedback(source)

        assert entity.energy is None
        assert entity.leg_freshness is None
        assert entity.motivation is None
        assert entity.recovery is None
        assert entity.biggest_limitation is None
        assert entity.notion_url is None

    def test_fk_field_reset_to_none_when_not_passed(self) -> None:
        existing = Feedback()
        existing.phase_id = 5

        source = _make_notion_feedback()
        result = map_feedback(source, existing)

        assert result.phase_id is None


# ===========================================================================
# NutritionGuideline mapper
# ===========================================================================


def _make_notion_nutrition(**overrides: object) -> NotionNutritionGuideline:
    defaults: dict[str, object] = {
        "notion_id": "nutrition-abc",
        "name": "Race Season Nutrition",
        "goal": "Performance",
        "applies_to": ["Race", "Training"],
        "carb_strategy": "High carb on race days",
        "protein_target_g_per_kg": "1.6-2.0",
        "fat_target_g_per_kg": "0.8-1.0",
        "hydration_electrolytes": "Sodium + potassium",
        "supplements": "Caffeine, beet root",
        "timing_rules": "Carbs 3h before",
        "url": "https://notion.so/nutrition-abc",
        "archived": False,
    }
    defaults.update(overrides)
    return NotionNutritionGuideline(**defaults)  # type: ignore[arg-type]


class TestMapNutritionGuideline:
    def test_create_new_entity(self) -> None:
        source = _make_notion_nutrition()
        entity = map_nutrition_guideline(source)

        assert isinstance(entity, NutritionGuideline)
        assert entity.notion_page_id == "nutrition-abc"
        assert entity.notion_url == "https://notion.so/nutrition-abc"
        assert entity.name == "Race Season Nutrition"
        assert entity.goal == "Performance"
        assert entity.applies_to == ["Race", "Training"]
        assert entity.carb_strategy == "High carb on race days"
        assert entity.protein_target_g_per_kg == "1.6-2.0"
        assert entity.fat_target_g_per_kg == "0.8-1.0"
        assert entity.hydration_electrolytes == "Sodium + potassium"
        assert entity.supplements == "Caffeine, beet root"
        assert entity.timing_rules == "Carbs 3h before"

    def test_update_existing_entity(self) -> None:
        existing = NutritionGuideline()
        existing.name = "Old Plan"
        existing.goal = "Base"

        source = _make_notion_nutrition(name="Updated Plan", goal="Performance")
        result = map_nutrition_guideline(source, existing)

        assert result is existing
        assert result.name == "Updated Plan"
        assert result.goal == "Performance"

    def test_none_values_are_propagated(self) -> None:
        source = _make_notion_nutrition(
            goal=None,
            carb_strategy=None,
            protein_target_g_per_kg=None,
            fat_target_g_per_kg=None,
            hydration_electrolytes=None,
            supplements=None,
            timing_rules=None,
            url=None,
        )
        entity = map_nutrition_guideline(source)

        assert entity.goal is None
        assert entity.carb_strategy is None
        assert entity.protein_target_g_per_kg is None
        assert entity.fat_target_g_per_kg is None
        assert entity.hydration_electrolytes is None
        assert entity.supplements is None
        assert entity.timing_rules is None
        assert entity.notion_url is None

    def test_applies_to_list_is_copied(self) -> None:
        applies = ["Race"]
        source = _make_notion_nutrition(applies_to=applies)
        entity = map_nutrition_guideline(source)

        applies.append("Training")
        assert entity.applies_to == ["Race"]

    def test_overwrite_all_fields_on_existing_entity(self) -> None:
        existing = NutritionGuideline()
        existing.notion_page_id = "old-id"
        existing.notion_url = "https://notion.so/old"
        existing.name = "Old"
        existing.goal = "Old goal"
        existing.applies_to = ["Old"]
        existing.carb_strategy = "Old strategy"

        source = _make_notion_nutrition()
        result = map_nutrition_guideline(source, existing)

        assert result.notion_page_id == "nutrition-abc"
        assert result.notion_url == "https://notion.so/nutrition-abc"
        assert result.name == "Race Season Nutrition"
        assert result.goal == "Performance"
        assert result.applies_to == ["Race", "Training"]
        assert result.carb_strategy == "High carb on race days"
