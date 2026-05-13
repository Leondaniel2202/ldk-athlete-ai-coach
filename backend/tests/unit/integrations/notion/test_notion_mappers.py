"""Unit tests for the Notion mapper layer."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ldk_athlete_ai_coach.core.integrations.notion.mappers.event import map_event
from ldk_athlete_ai_coach.core.integrations.notion.mappers.feedback import map_feedback
from ldk_athlete_ai_coach.core.integrations.notion.mappers.nutrition import map_nutrition
from ldk_athlete_ai_coach.core.integrations.notion.mappers.phase import map_phase
from ldk_athlete_ai_coach.core.integrations.notion.mappers.plan import map_plan
from ldk_athlete_ai_coach.core.integrations.notion.mappers.session import map_session
from ldk_athlete_ai_coach.core.integrations.notion.mappers.workout import map_workout
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
from ldk_athlete_ai_coach.db.models.training import (
    Event,
    Feedback,
    NutritionGuideline,
    Phase,
    Plan,
    TrackedSession,
    Workout,
)
from ldk_athlete_ai_coach.domain.enums.workout import WorkoutCategory

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_DT = datetime(2024, 3, 1, 8, 0, 0, tzinfo=UTC)
_DT2 = datetime(2024, 6, 30, 20, 0, 0, tzinfo=UTC)


# ===========================================================================
# Plan mapper
# ===========================================================================


def _make_notion_plan(**overrides: object) -> NotionPlan:
    defaults: dict[str, object] = {
        "notion_id": "plan-abc",
        "name": "Base Plan",
        "description": "Finish strong",
        "start_date": _DT.date(),
        "end_date": _DT2.date(),
        "notion_page_content": "Plan context",
        "url": "https://notion.so/plan-abc",
        "archived": False,
    }
    defaults.update(overrides)
    return NotionPlan(**defaults)  # type: ignore[arg-type]


class TestMapPlan:
    def test_create_new_entity(self) -> None:
        source = _make_notion_plan()
        entity = map_plan(source)

        assert isinstance(entity, Plan)
        assert entity.notion_page_id == "plan-abc"
        assert entity.notion_url == "https://notion.so/plan-abc"
        assert entity.notion_page_content == "Plan context"
        assert entity.name == "Base Plan"
        assert entity.description == "Finish strong"

    def test_update_existing_entity(self) -> None:
        existing = Plan()
        existing.name = "Old Plan"

        result = map_plan(_make_notion_plan(name="Updated Plan"), existing)

        assert result is existing
        assert result.name == "Updated Plan"


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
        "start_date": _DT.date(),
        "end_date": _DT2.date(),
        "plan_notion_id": "plan-xyz",
        "nutrition_guideline_notion_id": "nutrition-xyz",
        "notion_page_content": "Phase context",
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
        assert entity.notion_page_content == "Phase context"
        assert entity.name == "Base Phase"
        assert entity.notes == "Focus on aerobic base"
        assert entity.phase_type == "Base"
        assert entity.focus_tags == ["Endurance", "Aerobic"]
        assert entity.start_date == _DT.date()
        assert entity.end_date == _DT2.date()

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
            phase_type="Unknown",
            start_date=_DT.date(),
            end_date=_DT2.date(),
            url=None,
        )
        entity = map_phase(source)

        assert entity.notes is None
        assert entity.phase_type == "Unknown"
        assert entity.start_date == _DT.date()
        assert entity.end_date == _DT2.date()
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
        "planned_date": _DT.date(),
        "category": "Run",
        "difficulty": "Moderate",
        "equipment": ["Shoes"],
        "impact": "Low",
        "metrics_to_record": ["HR", "Pace"],
        "purpose": ["Aerobic"],
        "primary_muscle_groups": ["Legs"],
        "planned_distance_km": 10.0,
        "planned_duration_min": 60.0,
        "planned_rpe": 6.0,
        "planned_week_number": 3.0,
        "planned_week_start_date": _DT.date(),
        "actual_duration_min": 58.0,
        "actual_distance_km": 10.4,
        "actual_training_load": 389.0,
        "actual_calories_burned_kcal": 740.0,
        "weighted_hrr_intensity_sum": 141.2,
        "actual_hrr_intensity": 2.43,
        "actual_rpe": 5.5,
        "done_at": _DT,
        "session_count": 1,
        "status": "Done",
        "training_load_method": "Weighted HRR",
        "additional_info": "Easy effort",
        "cancelled": False,
        "skipped": False,
        "phase_notion_id": "phase-xyz",
        "notion_page_content": "Workout instructions",
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
        assert entity.notion_page_content == "Workout instructions"
        assert entity.name == "Morning Run"
        assert entity.planned_date == _DT.date()
        assert entity.category == "Run"
        assert entity.difficulty == "Moderate"
        assert entity.equipment == ["Shoes"]
        assert entity.impact == "Low"
        assert entity.metrics_to_record == ["HR", "Pace"]
        assert entity.purpose == ["Aerobic"]
        assert entity.primary_muscle_groups == ["Legs"]
        assert entity.planned_distance_km == pytest.approx(10.0)
        assert entity.planned_duration_min == pytest.approx(60.0)
        assert entity.planned_rpe == pytest.approx(6.0)
        assert entity.planned_training_load == pytest.approx(360.0)
        assert entity.planned_week_number == pytest.approx(3.0)
        assert entity.planned_week_start_date == _DT.date()
        assert entity.actual_duration_min == pytest.approx(58.0)
        assert entity.actual_distance_km == pytest.approx(10.4)
        assert entity.actual_training_load == pytest.approx(389.0)
        assert entity.actual_calories_burned_kcal == pytest.approx(740.0)
        assert entity.weighted_hrr_intensity_sum == pytest.approx(141.2)
        assert entity.actual_hrr_intensity == pytest.approx(2.43)
        assert entity.actual_rpe == pytest.approx(5.5)
        assert entity.done_date_start == _DT
        assert entity.done_date_end is None
        assert entity.done_date_is_datetime is True
        assert entity.status == "Done"
        assert entity.training_load_method == "Weighted HRR"
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
        existing.category = WorkoutCategory.BOXING

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
            planned_date=None,
            category="Unknown",
            difficulty=None,
            impact=None,
            planned_distance_km=None,
            planned_duration_min=None,
            planned_rpe=None,
            planned_week_number=None,
            actual_duration_min=None,
            actual_distance_km=None,
            actual_training_load=None,
            actual_calories_burned_kcal=None,
            weighted_hrr_intensity_sum=None,
            actual_hrr_intensity=None,
            actual_rpe=None,
            done_at=None,
            session_count=0,
            status=None,
            training_load_method=None,
            additional_info=None,
            url=None,
        )
        entity = map_workout(source)

        assert entity.planned_date is None
        assert entity.category == "Unknown"
        assert entity.difficulty is None
        assert entity.impact is None
        assert entity.planned_distance_km is None
        assert entity.planned_duration_min is None
        assert entity.planned_rpe is None
        assert entity.planned_training_load is None
        assert entity.planned_week_number is None
        assert entity.actual_duration_min is None
        assert entity.actual_distance_km is None
        assert entity.actual_training_load is None
        assert entity.actual_calories_burned_kcal is None
        assert entity.weighted_hrr_intensity_sum is None
        assert entity.actual_hrr_intensity is None
        assert entity.actual_rpe is None
        assert entity.done_date_start is None
        assert entity.done_date_end is None
        assert entity.status is None
        assert entity.training_load_method is None
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
# Event mapper
# ===========================================================================


def _make_notion_event(**overrides: object) -> NotionEvent:
    defaults: dict[str, object] = {
        "notion_id": "event-abc",
        "name": "Goal Race",
        "event_type": "Race",
        "sport": "Run",
        "status": "Planned",
        "target": "Sub-3 marathon",
        "event_format": "Road marathon",
        "notes": "Primary event",
        "priority": "A",
        "start_at": _DT,
        "end_at": _DT2,
        "location": "Amsterdam",
        "plan_notion_id": "plan-xyz",
        "race_workout_notion_id": "workout-xyz",
        "notion_page_content": "Event context",
        "url": "https://notion.so/event-abc",
        "archived": False,
    }
    defaults.update(overrides)
    return NotionEvent(**defaults)  # type: ignore[arg-type]


class TestMapEvent:
    def test_create_new_entity(self) -> None:
        source = _make_notion_event()
        entity = map_event(source, plan_id=7, race_workout_id=11)

        assert isinstance(entity, Event)
        assert entity.notion_page_id == "event-abc"
        assert entity.notion_url == "https://notion.so/event-abc"
        assert entity.notion_page_content == "Event context"
        assert entity.event_type == "Race"
        assert entity.location == "Amsterdam"
        assert entity.plan_id == 7
        assert entity.race_workout_id == 11

    def test_update_existing_entity(self) -> None:
        existing = Event()
        existing.name = "Old Event"
        existing.priority = "C"  # type: ignore[assignment]

        result = map_event(_make_notion_event(name="Updated Event", priority="A"), existing)

        assert result is existing
        assert result.name == "Updated Event"
        assert result.priority == "A"

    def test_foreign_keys_reset_to_none_when_not_passed(self) -> None:
        existing = Event()
        existing.plan_id = 9
        existing.race_workout_id = 4

        result = map_event(_make_notion_event(), existing)

        assert result.plan_id is None
        assert result.race_workout_id is None


# ===========================================================================
# NutritionGuideline mapper
# ===========================================================================


def _make_notion_nutrition(**overrides: object) -> NotionNutritionGuideline:
    defaults: dict[str, object] = {
        "notion_id": "nutrition-abc",
        "name": "Performance Fueling",
        "goal": "Performance",
        "applies_to": ["Endurance", "Hybrid"],
        "carb_strategy": "Fuel key sessions",
        "protein_target_g_per_kg": "1.8",
        "fat_target_g_per_kg": "0.8",
        "hydration_electrolytes": "500-750ml/hr",
        "supplements": "Creatine",
        "timing_rules": "Carbs before and during sessions",
        "notion_page_content": "Nutrition context",
        "url": "https://notion.so/nutrition-abc",
        "archived": False,
    }
    defaults.update(overrides)
    return NotionNutritionGuideline(**defaults)  # type: ignore[arg-type]


class TestMapNutritionGuideline:
    def test_create_new_entity(self) -> None:
        source = _make_notion_nutrition()
        entity = map_nutrition(source)

        assert isinstance(entity, NutritionGuideline)
        assert entity.notion_page_id == "nutrition-abc"
        assert entity.notion_url == "https://notion.so/nutrition-abc"
        assert entity.notion_page_content == "Nutrition context"
        assert entity.goal == "Performance"
        assert entity.applies_to == ["Endurance", "Hybrid"]
        assert entity.timing_rules == "Carbs before and during sessions"

    def test_update_existing_entity(self) -> None:
        existing = NutritionGuideline()
        existing.name = "Old Guideline"
        existing.goal = "Maintain"

        result = map_nutrition(
            _make_notion_nutrition(name="Updated Guideline", goal="Gain"), existing
        )

        assert result is existing
        assert result.name == "Updated Guideline"
        assert result.goal == "Gain"

    def test_list_field_is_copied(self) -> None:
        applies_to = ["Endurance"]
        entity = map_nutrition(_make_notion_nutrition(applies_to=applies_to))

        applies_to.append("Strength")
        assert entity.applies_to == ["Endurance"]

    def test_none_values_are_propagated(self) -> None:
        entity = map_nutrition(
            _make_notion_nutrition(
                goal=None,
                carb_strategy=None,
                protein_target_g_per_kg=None,
                hydration_electrolytes=None,
                supplements=None,
                timing_rules=None,
                url=None,
            )
        )

        assert entity.goal is None
        assert entity.carb_strategy is None
        assert entity.timing_rules is None
        assert entity.notion_url is None


# ===========================================================================
# Feedback mapper
# ===========================================================================


def _make_notion_feedback(**overrides: object) -> NotionWeeklyFeedback:
    defaults: dict[str, object] = {
        "notion_id": "feedback-abc",
        "name": "2024-W10",
        "week": "2024-W10",
        "energy": 4.0,
        "leg_freshness": 3.5,
        "motivation": 5.0,
        "recovery": 4.5,
        "biggest_limitation": "Time",
        "phase_notion_id": "phase-xyz",
        "notion_page_content": "Feedback notes",
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
        assert entity.notion_page_content == "Feedback notes"
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
# TrackedSession mapper
# ===========================================================================


def _make_notion_session(**overrides: object) -> NotionSession:
    defaults: dict[str, object] = {
        "notion_id": "session-abc",
        "name": "Morning Run",
        "source": "Apple Health",
        "session_type": "Running",
        "external_id": "ext-123",
        "start_at": _DT,
        "end_at": _DT2,
        "actual_rpe": 6.0,
        "active_energy_kj": 1200.0,
        "active_energy_burned_kj": 1100.0,
        "avg_hr": 145.0,
        "max_hr": 175.0,
        "calories_kcal": 500.0,
        "distance_km": 10.5,
        "duration_min": 60.0,
        "elevation_ascended_m": 120.0,
        "elevation_descended_m": 115.0,
        "intensity_kcal_per_hr_kg": 8.5,
        "step_cadence_count_per_min": 170.0,
        "steps": 9800.0,
        "workout_notion_id": "workout-xyz",
        "notion_page_content": "Session notes",
        "url": "https://notion.so/session-abc",
        "archived": False,
    }
    defaults.update(overrides)
    return NotionSession(**defaults)  # type: ignore[arg-type]


class TestMapSession:
    def test_create_new_entity(self) -> None:
        source = _make_notion_session()
        entity = map_session(source)

        assert isinstance(entity, TrackedSession)
        assert entity.notion_page_id == "session-abc"
        assert entity.notion_url == "https://notion.so/session-abc"
        assert entity.notion_page_content == "Session notes"
        assert entity.name == "Morning Run"
        assert entity.source == "Apple Health"
        assert entity.session_type == "Running"
        assert entity.external_id == "ext-123"
        assert entity.start_at == _DT
        assert entity.end_at == _DT2
        assert entity.actual_rpe == pytest.approx(6.0)
        assert entity.active_energy_kj == pytest.approx(1200.0)
        assert entity.active_energy_burned_kj == pytest.approx(1100.0)
        assert entity.avg_hr == pytest.approx(145.0)
        assert entity.max_hr == pytest.approx(175.0)
        assert entity.calories_kcal == pytest.approx(500.0)
        assert entity.distance_km == pytest.approx(10.5)
        assert entity.duration_min == pytest.approx(60.0)
        assert entity.elevation_ascended_m == pytest.approx(120.0)
        assert entity.elevation_descended_m == pytest.approx(115.0)
        assert entity.intensity_kcal_per_hr_kg == pytest.approx(8.5)
        assert entity.step_cadence_count_per_min == pytest.approx(170.0)
        assert entity.steps == pytest.approx(9800.0)

    def test_create_new_entity_has_no_workout_id_by_default(self) -> None:
        source = _make_notion_session()
        entity = map_session(source)

        assert entity.workout_id is None

    def test_scalar_foreign_key_workout_id_is_assigned(self) -> None:
        source = _make_notion_session()
        entity = map_session(source, workout_id=42)

        assert entity.workout_id == 42

    def test_update_existing_entity(self) -> None:
        existing = TrackedSession()
        existing.name = "Old Session"
        existing.avg_hr = 130.0

        source = _make_notion_session(name="Updated Session", avg_hr=150.0)
        result = map_session(source, existing)

        assert result is existing
        assert result.name == "Updated Session"
        assert result.avg_hr == pytest.approx(150.0)

    def test_overwrite_existing_workout_id(self) -> None:
        existing = TrackedSession()
        existing.workout_id = 99

        source = _make_notion_session()
        result = map_session(source, existing, workout_id=7)

        assert result.workout_id == 7

    def test_none_values_are_propagated(self) -> None:
        source = _make_notion_session(
            source="Unknown",
            session_type="Unknown",
            external_id=None,
            start_at=_DT,
            end_at=None,
            avg_hr=None,
            max_hr=None,
            distance_km=None,
            duration_min=None,
            url=None,
        )
        entity = map_session(source)

        assert entity.source == "Unknown"
        assert entity.session_type == "Unknown"
        assert entity.external_id is None
        assert entity.start_at == _DT
        assert entity.end_at is None
        assert entity.avg_hr is None
        assert entity.max_hr is None
        assert entity.distance_km is None
        assert entity.duration_min is None
        assert entity.notion_url is None

    def test_fk_field_reset_to_none_when_not_passed(self) -> None:
        existing = TrackedSession()
        existing.workout_id = 5

        source = _make_notion_session()
        result = map_session(source, existing)

        assert result.workout_id is None
