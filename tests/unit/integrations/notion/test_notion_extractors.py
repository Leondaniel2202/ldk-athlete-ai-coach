"""Unit tests for the Notion extraction layer."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from ldk_athlete_ai_coach.core.integrations.notion.extractors import NotionExtractionError
from ldk_athlete_ai_coach.core.integrations.notion.extractors.event_extractor import extract_event
from ldk_athlete_ai_coach.core.integrations.notion.extractors.nutrition_guideline_extractor import (
    extract_nutrition_guideline,
)
from ldk_athlete_ai_coach.core.integrations.notion.extractors.phase_extractor import extract_phase
from ldk_athlete_ai_coach.core.integrations.notion.extractors.session_extractor import (
    extract_session,
)
from ldk_athlete_ai_coach.core.integrations.notion.extractors.weekly_feedback_extractor import (
    extract_weekly_feedback,
)
from ldk_athlete_ai_coach.core.integrations.notion.extractors.workout_extractor import (
    extract_workout,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _title_prop(text: str) -> dict[str, Any]:
    return {"type": "title", "title": [{"plain_text": text}]}


def _rich_text_prop(text: str) -> dict[str, Any]:
    return {"type": "rich_text", "rich_text": [{"plain_text": text}]}


def _select_prop(name: str) -> dict[str, Any]:
    return {"type": "select", "select": {"name": name}}


def _multi_select_prop(*names: str) -> dict[str, Any]:
    return {"type": "multi_select", "multi_select": [{"name": n} for n in names]}


def _number_prop(value: float) -> dict[str, Any]:
    return {"type": "number", "number": value}


def _url_prop(value: str) -> dict[str, Any]:
    return {"type": "url", "url": value}


def _formula_number_prop(value: float | None) -> dict[str, Any]:
    return {"type": "formula", "formula": {"type": "number", "number": value}}


def _formula_string_prop(value: str | None) -> dict[str, Any]:
    return {"type": "formula", "formula": {"type": "string", "string": value}}


def _rollup_number_prop(value: float | None) -> dict[str, Any]:
    return {"type": "rollup", "rollup": {"type": "number", "number": value}}


def _rollup_date_prop(start: str | None, end: str | None = None) -> dict[str, Any]:
    return {
        "type": "rollup",
        "rollup": {
            "type": "date",
            "date": None if start is None else {"start": start, "end": end},
        },
    }


def _checkbox_prop(value: bool) -> dict[str, Any]:
    return {"type": "checkbox", "checkbox": value}


def _date_prop(start: str, end: str | None = None) -> dict[str, Any]:
    return {"type": "date", "date": {"start": start, "end": end}}


def _relation_prop(*page_ids: str) -> dict[str, Any]:
    return {"type": "relation", "relation": [{"id": pid} for pid in page_ids]}


def _place_prop(
    *,
    name: str,
    address: str,
    latitude: float,
    longitude: float,
    google_place_id: str,
) -> dict[str, Any]:
    return {
        "type": "place",
        "place": {
            "name": name,
            "address": address,
            "latitude": latitude,
            "longitude": longitude,
            "google_place_id": google_place_id,
        },
    }


def _empty_prop(type_: str) -> dict[str, Any]:
    """Return a property whose value is null / empty for its type."""
    mapping: dict[str, Any] = {
        "title": {"type": "title", "title": []},
        "rich_text": {"type": "rich_text", "rich_text": []},
        "select": {"type": "select", "select": None},
        "multi_select": {"type": "multi_select", "multi_select": []},
        "number": {"type": "number", "number": None},
        "checkbox": {"type": "checkbox", "checkbox": False},
        "date": {"type": "date", "date": None},
        "relation": {"type": "relation", "relation": []},
        "place": {"type": "place", "place": None},
        "url": {"type": "url", "url": None},
    }
    return mapping[type_]


# ---------------------------------------------------------------------------
# Sample raw Notion pages
# ---------------------------------------------------------------------------

_PHASE_PAGE: dict[str, Any] = {
    "id": "phase-page-id",
    "object": "page",
    "created_time": "2024-01-10T08:00:00.000Z",
    "last_edited_time": "2024-01-15T12:00:00.000Z",
    "archived": False,
    "url": "https://www.notion.so/phase-page-id",
    "properties": {
        "Name": _title_prop("Base Phase"),
        "Notes": _rich_text_prop("Focus on aerobic base"),
        "Phase type": _select_prop("Base"),
        "Focus tags": _multi_select_prop("Endurance", "Aerobic"),
        "Weekly structure": _rich_text_prop("Mon: Run, Wed: Bike, Fri: Run"),
        "Timeframe": _date_prop("2024-02-01", "2024-03-15"),
        "Plan": _relation_prop("plan-page-id"),
        "Nutrition Guidelines": _relation_prop("nutrition-page-id"),
    },
}

_WORKOUT_PAGE: dict[str, Any] = {
    "id": "workout-page-id",
    "object": "page",
    "created_time": "2024-01-20T09:00:00.000Z",
    "last_edited_time": "2024-01-20T10:00:00.000Z",
    "archived": False,
    "url": "https://www.notion.so/workout-page-id",
    "properties": {
        "Name": _title_prop("Long Run"),
        "Planned Date": _date_prop("2024-02-05"),
        "Category": _select_prop("Run"),
        "Difficulty": _select_prop("3 - Moderate"),
        "Equipment": _multi_select_prop("Shoes", "HR Monitor"),
        "Impact": _select_prop("High"),
        "Metrics to record": _multi_select_prop("Heart Rate", "Pace"),
        "Purpose": _multi_select_prop("Aerobic"),
        "Primarily used muscle group": _multi_select_prop("Legs"),
        "Planned Distance (km)": _number_prop(20.0),
        "Planned duration (min)": _number_prop(110.0),
        "Planned RPE": _number_prop(6.0),
        "Planned Training Load": _formula_number_prop(660.0),
        "Planned Week Number": _number_prop(3.0),
        "Actual Duration (min)": _rollup_number_prop(108.0),
        "Actual Distance": _rollup_number_prop(20.1),
        "Actual Training Load": _rollup_number_prop(705.0),
        "Actual calories burned (kcal)": _rollup_number_prop(1450.0),
        "Weighted HRR Intensity Sum": _rollup_number_prop(312.4),
        "Actual HRR Intensity": _formula_number_prop(2.89),
        "Actual RPE": _number_prop(7.0),
        "Done Date": _rollup_date_prop("2024-02-05T08:55:00+00:00"),
        "Status": _formula_string_prop("Done"),
        "Training Load Method": _formula_string_prop("Weighted HRR"),
        "Additional Info": _url_prop("https://example.com/workouts/long-run"),
        "Cancelled": _checkbox_prop(False),
        "Skipped": _checkbox_prop(False),
        "Phase": _relation_prop("phase-page-id"),
    },
}

_EVENT_PAGE: dict[str, Any] = {
    "id": "event-page-id",
    "object": "page",
    "created_time": "2024-01-10T08:00:00.000Z",
    "last_edited_time": "2024-01-15T12:00:00.000Z",
    "archived": False,
    "url": "https://www.notion.so/event-page-id",
    "properties": {
        "Name": _title_prop("Goal Race"),
        "Type": _select_prop("Race"),
        "Target": _rich_text_prop("Sub-3 marathon"),
        "Format": _rich_text_prop("Road marathon"),
        "Notes": _rich_text_prop("Primary A race"),
        "Priority": _select_prop("A"),
        "Start date": _date_prop("2024-10-20"),
        "End date": _date_prop("2024-10-20"),
        "Place": _place_prop(
            name="Amsterdam",
            address="Museumplein, Amsterdam",
            latitude=52.3584,
            longitude=4.8811,
            google_place_id="place-123",
        ),
        "Plan": _relation_prop("plan-page-id"),
        "Race Workout": _relation_prop("workout-page-id"),
    },
}

_SESSION_PAGE: dict[str, Any] = {
    "id": "session-page-id",
    "object": "page",
    "created_time": "2024-02-05T06:00:00.000Z",
    "last_edited_time": "2024-02-05T08:30:00.000Z",
    "archived": False,
    "url": "https://www.notion.so/session-page-id",
    "properties": {
        "Name": _title_prop("Morning Run 2024-02-05"),
        "Source": _select_prop("Apple Health"),
        "Session Type": _select_prop("Running"),
        "External ID": _rich_text_prop("ext-abc123"),
        "Start": _date_prop("2024-02-05T06:00:00+00:00"),
        "End": _date_prop("2024-02-05T08:00:00+00:00"),
        "Active Energy (kJ)": _number_prop(2500.0),
        "Active Energy Burned (kJ)": _number_prop(2450.0),
        "Avg HR": _number_prop(148.0),
        "Max HR": _number_prop(175.0),
        "Calories (kcal)": _number_prop(598.0),
        "Distance (km)": _number_prop(20.2),
        "Duration (min)": _number_prop(109.5),
        "Elevation Ascended (m)": _number_prop(120.0),
        "Elevation Descended (m)": _number_prop(118.0),
        "Intensity (kcal/hr/kg)": _number_prop(5.4),
        "Step Cadence (count/min)": _number_prop(172.0),
        "Steps": _number_prop(18900.0),
        "Workout": _relation_prop("workout-page-id"),
    },
}

_NUTRITION_PAGE: dict[str, Any] = {
    "id": "nutrition-page-id",
    "object": "page",
    "created_time": "2024-01-10T08:00:00.000Z",
    "last_edited_time": "2024-01-15T12:00:00.000Z",
    "archived": False,
    "url": "https://www.notion.so/nutrition-page-id",
    "properties": {
        "Name": _title_prop("Performance Fueling"),
        "Goal": _select_prop("Performance"),
        "Applies to": _multi_select_prop("Endurance", "Hybrid"),
        "Carb strategy": _rich_text_prop("Fuel hard sessions aggressively"),
        "Protein target (g/kg)": _rich_text_prop("1.8"),
        "Fat target (g/kg)": _rich_text_prop("0.8"),
        "Hydration / electrolytes": _rich_text_prop("500-750ml/hr with sodium"),
        "Supplements": _rich_text_prop("Creatine, caffeine"),
        "Timing rules": _rich_text_prop("Carbs before and during key sessions"),
    },
}

_FEEDBACK_PAGE: dict[str, Any] = {
    "id": "feedback-page-id",
    "object": "page",
    "created_time": "2024-02-12T20:00:00.000Z",
    "last_edited_time": "2024-02-12T20:05:00.000Z",
    "archived": False,
    "url": "https://www.notion.so/feedback-page-id",
    "properties": {
        "Week": _title_prop("Week 3"),
        "Energy": _number_prop(7.0),
        "Leg Freshness": _number_prop(6.0),
        "Motivation": _number_prop(8.0),
        "Recovery": _number_prop(7.5),
        "Biggest Limitation": _select_prop("Sleep"),
        "Phase": _relation_prop("phase-page-id"),
    },
}


# ===========================================================================
# extract_phase
# ===========================================================================


class TestExtractPhase:
    def test_full_payload_extracts_correctly(self) -> None:
        phase = extract_phase(_PHASE_PAGE)

        assert phase.notion_id == "phase-page-id"
        assert phase.name == "Base Phase"
        assert phase.notes == "Focus on aerobic base"
        assert phase.phase_type == "Base"
        assert phase.focus_tags == ["Endurance", "Aerobic"]
        assert phase.weekly_structure == "Mon: Run, Wed: Bike, Fri: Run"
        assert phase.timeframe_start == datetime(2024, 2, 1, 0, 0)
        assert phase.timeframe_end == datetime(2024, 3, 15, 0, 0)
        assert phase.timeframe_is_datetime is False
        assert phase.plan_notion_id == "plan-page-id"
        assert phase.nutrition_guideline_notion_id == "nutrition-page-id"
        assert phase.created_time == datetime(2024, 1, 10, 8, 0, tzinfo=UTC)
        assert phase.archived is False
        assert phase.url == "https://www.notion.so/phase-page-id"

    def test_optional_fields_absent(self) -> None:
        page: dict[str, Any] = {
            **_PHASE_PAGE,
            "properties": {
                "Name": _title_prop("Minimal Phase"),
                "Notes": _empty_prop("rich_text"),
                "Phase type": _empty_prop("select"),
                "Focus tags": _empty_prop("multi_select"),
                "Weekly structure": _empty_prop("rich_text"),
                "Timeframe": _empty_prop("date"),
                "Plan": _empty_prop("relation"),
                "Nutrition Guidelines": _empty_prop("relation"),
            },
        }
        phase = extract_phase(page)

        assert phase.name == "Minimal Phase"
        assert phase.notes is None
        assert phase.phase_type is None
        assert phase.focus_tags == []
        assert phase.weekly_structure is None
        assert phase.timeframe_start is None
        assert phase.timeframe_end is None
        assert phase.plan_notion_id is None
        assert phase.nutrition_guideline_notion_id is None

    def test_legacy_property_aliases_supported(self) -> None:
        page: dict[str, Any] = {
            **_PHASE_PAGE,
            "properties": {
                "Name": _title_prop("Legacy Phase"),
                "Notes": _rich_text_prop("Legacy naming still syncs"),
                "Phase Type": _select_prop("Base"),
                "Focus Tags": _multi_select_prop("Endurance", "Aerobic"),
                "Weekly Structure": _rich_text_prop("Mon: Run, Wed: Bike, Fri: Run"),
                "Timeframe": _date_prop("2024-02-01", "2024-03-15"),
                "Plan": _relation_prop("plan-page-id"),
                "Nutrition Guideline": _relation_prop("nutrition-page-id"),
            },
        }

        phase = extract_phase(page)

        assert phase.name == "Legacy Phase"
        assert phase.phase_type == "Base"
        assert phase.focus_tags == ["Endurance", "Aerobic"]
        assert phase.weekly_structure == "Mon: Run, Wed: Bike, Fri: Run"
        assert phase.nutrition_guideline_notion_id == "nutrition-page-id"

    def test_missing_name_raises_extraction_error(self) -> None:
        page: dict[str, Any] = {**_PHASE_PAGE, "properties": {"Name": _empty_prop("title")}}
        with pytest.raises(NotionExtractionError, match="missing required 'Name'"):
            extract_phase(page)

    def test_missing_id_key_raises_extraction_error(self) -> None:
        page = {k: v for k, v in _PHASE_PAGE.items() if k != "id"}
        with pytest.raises(NotionExtractionError):
            extract_phase(page)

    def test_timeframe_datetime_flag(self) -> None:
        page: dict[str, Any] = {
            **_PHASE_PAGE,
            "properties": {
                **_PHASE_PAGE["properties"],
                "Timeframe": _date_prop("2024-02-01T06:00:00+00:00", "2024-02-28T06:00:00+00:00"),
            },
        }
        phase = extract_phase(page)
        assert phase.timeframe_is_datetime is True

    def test_multiple_relations_uses_first(self) -> None:
        page: dict[str, Any] = {
            **_PHASE_PAGE,
            "properties": {
                **_PHASE_PAGE["properties"],
                "Plan": _relation_prop("first-plan-id", "second-plan-id"),
            },
        }
        phase = extract_phase(page)
        assert phase.plan_notion_id == "first-plan-id"

    def test_archived_flag_propagated(self) -> None:
        page = {**_PHASE_PAGE, "archived": True}
        phase = extract_phase(page)
        assert phase.archived is True


# ===========================================================================
# extract_workout
# ===========================================================================


class TestExtractWorkout:
    def test_full_payload_extracts_correctly(self) -> None:
        workout = extract_workout(_WORKOUT_PAGE)

        assert workout.notion_id == "workout-page-id"
        assert workout.name == "Long Run"
        assert workout.date_start == datetime(2024, 2, 5, 0, 0)
        assert workout.date_end is None
        assert workout.date_is_datetime is False
        assert workout.category == "Run"
        assert workout.difficulty == "3 - Moderate"
        assert workout.equipment == ["Shoes", "HR Monitor"]
        assert workout.impact == "High"
        assert workout.metrics_to_record == ["Heart Rate", "Pace"]
        assert workout.purpose == ["Aerobic"]
        assert workout.primarily_used_muscle_group == ["Legs"]
        assert workout.planned_distance_km == 20.0
        assert workout.planned_duration_min == 110.0
        assert workout.planned_rpe == 6.0
        assert workout.planned_training_load == 660.0
        assert workout.planned_week_number == 3.0
        assert workout.actual_duration_min == 108.0
        assert workout.actual_distance_km == 20.1
        assert workout.actual_training_load == 705.0
        assert workout.actual_calories_burned_kcal == 1450.0
        assert workout.weighted_hrr_intensity_sum == 312.4
        assert workout.actual_hrr_intensity == 2.89
        assert workout.actual_rpe == 7.0
        assert workout.done_date_start == datetime(2024, 2, 5, 8, 55, tzinfo=UTC)
        assert workout.done_date_end is None
        assert workout.done_date_is_datetime is True
        assert workout.status == "Done"
        assert workout.training_load_method == "Weighted HRR"
        assert workout.additional_info == "https://example.com/workouts/long-run"
        assert workout.cancelled is False
        assert workout.skipped is False
        assert workout.phase_notion_id == "phase-page-id"
        assert workout.url == "https://www.notion.so/workout-page-id"

    def test_optional_fields_absent(self) -> None:
        page: dict[str, Any] = {
            **_WORKOUT_PAGE,
            "properties": {
                "Name": _title_prop("Minimal Workout"),
                "Planned Date": _empty_prop("date"),
                "Category": _empty_prop("select"),
                "Difficulty": _empty_prop("select"),
                "Equipment": _empty_prop("multi_select"),
                "Impact": _empty_prop("select"),
                "Metrics to record": _empty_prop("multi_select"),
                "Purpose": _empty_prop("multi_select"),
                "Primarily used muscle group": _empty_prop("multi_select"),
                "Planned Distance (km)": _empty_prop("number"),
                "Planned duration (min)": _empty_prop("number"),
                "Planned RPE": _empty_prop("number"),
                "Planned Training Load": _formula_number_prop(None),
                "Planned Week Number": _empty_prop("number"),
                "Actual Duration (min)": _rollup_number_prop(None),
                "Actual Distance": _rollup_number_prop(None),
                "Actual Training Load": _rollup_number_prop(None),
                "Actual calories burned (kcal)": _rollup_number_prop(None),
                "Weighted HRR Intensity Sum": _rollup_number_prop(None),
                "Actual HRR Intensity": _formula_number_prop(None),
                "Actual RPE": _empty_prop("number"),
                "Done Date": _rollup_date_prop(None),
                "Status": _formula_string_prop(None),
                "Training Load Method": _formula_string_prop(None),
                "Additional Info": _empty_prop("url"),
                "Cancelled": _empty_prop("checkbox"),
                "Skipped": _empty_prop("checkbox"),
                "Phase": _empty_prop("relation"),
            },
        }
        workout = extract_workout(page)

        assert workout.name == "Minimal Workout"
        assert workout.date_start is None
        assert workout.category is None
        assert workout.equipment == []
        assert workout.planned_distance_km is None
        assert workout.planned_training_load is None
        assert workout.actual_duration_min is None
        assert workout.actual_distance_km is None
        assert workout.actual_training_load is None
        assert workout.actual_calories_burned_kcal is None
        assert workout.weighted_hrr_intensity_sum is None
        assert workout.actual_hrr_intensity is None
        assert workout.done_date_start is None
        assert workout.status is None
        assert workout.training_load_method is None
        assert workout.additional_info is None
        assert workout.cancelled is False
        assert workout.phase_notion_id is None

    def test_property_aliases_supported(self) -> None:
        page: dict[str, Any] = {
            **_WORKOUT_PAGE,
            "properties": {
                "Name": _title_prop("Legacy Workout"),
                "Planned Date": _date_prop("2024-02-05"),
                "Category": _select_prop("Run"),
                "Difficulty": _select_prop("Moderate"),
                "Equipment": _multi_select_prop("Shoes"),
                "Impact": _select_prop("High"),
                "Metrics to Record": _multi_select_prop("HR", "Pace"),
                "Purpose": _multi_select_prop("Aerobic Capacity"),
                "Primarily Used Muscle Group": _multi_select_prop("Legs"),
                "Planned Distance (km)": _number_prop(18.0),
                "Planned Duration (min)": _number_prop(95.0),
                "Planned RPE": _number_prop(5.0),
                "Planned Week Number": _number_prop(2.0),
                "Actual RPE": _number_prop(6.0),
                "Additional Info": _rich_text_prop("Legacy text content"),
                "Cancelled": _checkbox_prop(False),
                "Skipped": _checkbox_prop(False),
                "Phase": _relation_prop("phase-page-id"),
            },
        }

        workout = extract_workout(page)

        assert workout.name == "Legacy Workout"
        assert workout.date_start == datetime(2024, 2, 5, 0, 0)
        assert workout.metrics_to_record == ["HR", "Pace"]
        assert workout.primarily_used_muscle_group == ["Legs"]
        assert workout.planned_duration_min == 95.0
        assert workout.additional_info == "Legacy text content"

    def test_missing_name_raises_extraction_error(self) -> None:
        page: dict[str, Any] = {**_WORKOUT_PAGE, "properties": {"Name": _empty_prop("title")}}
        with pytest.raises(NotionExtractionError, match="missing required 'Name'"):
            extract_workout(page)

    def test_date_with_range_and_datetime_flag(self) -> None:
        page: dict[str, Any] = {
            **_WORKOUT_PAGE,
            "properties": {
                **_WORKOUT_PAGE["properties"],
                "Planned Date": _date_prop(
                    "2024-02-05T07:00:00+00:00", "2024-02-05T09:00:00+00:00"
                ),
            },
        }
        workout = extract_workout(page)
        assert workout.date_is_datetime is True
        assert workout.date_end is not None

    def test_cancelled_checkbox_true(self) -> None:
        page: dict[str, Any] = {
            **_WORKOUT_PAGE,
            "properties": {**_WORKOUT_PAGE["properties"], "Cancelled": _checkbox_prop(True)},
        }
        workout = extract_workout(page)
        assert workout.cancelled is True

    def test_missing_id_key_raises_extraction_error(self) -> None:
        page = {k: v for k, v in _WORKOUT_PAGE.items() if k != "id"}
        with pytest.raises(NotionExtractionError):
            extract_workout(page)

    def test_malformed_properties_raises_extraction_error(self) -> None:
        page: dict[str, Any] = {**_WORKOUT_PAGE, "properties": "not-a-dict"}
        with pytest.raises(NotionExtractionError):
            extract_workout(page)


# ===========================================================================
# extract_event
# ===========================================================================


class TestExtractEvent:
    def test_full_payload_extracts_correctly(self) -> None:
        event = extract_event(_EVENT_PAGE)

        assert event.notion_id == "event-page-id"
        assert event.name == "Goal Race"
        assert event.event_type == "Race"
        assert event.target == "Sub-3 marathon"
        assert event.event_format == "Road marathon"
        assert event.notes == "Primary A race"
        assert event.priority == "A"
        assert event.start_date_start == datetime(2024, 10, 20, 0, 0)
        assert event.end_date_start == datetime(2024, 10, 20, 0, 0)
        assert event.place_name == "Amsterdam"
        assert event.place_address == "Museumplein, Amsterdam"
        assert event.place_latitude == pytest.approx(52.3584)
        assert event.place_longitude == pytest.approx(4.8811)
        assert event.place_google_place_id == "place-123"
        assert event.plan_notion_id == "plan-page-id"
        assert event.race_workout_notion_id == "workout-page-id"
        assert event.created_time == datetime(2024, 1, 10, 8, 0, tzinfo=UTC)

    def test_optional_fields_absent(self) -> None:
        page: dict[str, Any] = {
            **_EVENT_PAGE,
            "properties": {
                "Name": _title_prop("Minimal Event"),
                "Type": _empty_prop("select"),
                "Target": _empty_prop("rich_text"),
                "Format": _empty_prop("rich_text"),
                "Notes": _empty_prop("rich_text"),
                "Priority": _empty_prop("select"),
                "Start date": _empty_prop("date"),
                "End date": _empty_prop("date"),
                "Place": _empty_prop("place"),
                "Plan": _empty_prop("relation"),
                "Race Workout": _empty_prop("relation"),
            },
        }

        event = extract_event(page)

        assert event.event_type is None
        assert event.target is None
        assert event.event_format is None
        assert event.notes is None
        assert event.priority is None
        assert event.place_name is None
        assert event.plan_notion_id is None
        assert event.race_workout_notion_id is None

    def test_missing_name_raises_extraction_error(self) -> None:
        page: dict[str, Any] = {**_EVENT_PAGE, "properties": {"Name": _empty_prop("title")}}
        with pytest.raises(NotionExtractionError, match="missing required 'Name'"):
            extract_event(page)


# ===========================================================================
# extract_session
# ===========================================================================


class TestExtractSession:
    def test_full_payload_extracts_correctly(self) -> None:
        session = extract_session(_SESSION_PAGE)

        assert session.notion_id == "session-page-id"
        assert session.name == "Morning Run 2024-02-05"
        assert session.source == "Apple Health"
        assert session.session_type == "Running"
        assert session.external_id == "ext-abc123"
        assert session.start_is_datetime is True
        assert session.end_is_datetime is True
        assert session.active_energy_kj == 2500.0
        assert session.avg_hr == 148.0
        assert session.max_hr == 175.0
        assert session.calories_kcal == 598.0
        assert session.distance_km == 20.2
        assert session.duration_min == 109.5
        assert session.elevation_ascended_m == 120.0
        assert session.steps == 18900.0
        assert session.workout_notion_id == "workout-page-id"
        assert session.url == "https://www.notion.so/session-page-id"

    def test_optional_fields_absent(self) -> None:
        page: dict[str, Any] = {
            **_SESSION_PAGE,
            "properties": {
                "Name": _title_prop("Minimal Session"),
                "Source": _empty_prop("select"),
                "Session Type": _empty_prop("select"),
                "External ID": _empty_prop("rich_text"),
                "Start": _empty_prop("date"),
                "End": _empty_prop("date"),
                "Active Energy (kJ)": _empty_prop("number"),
                "Active Energy Burned (kJ)": _empty_prop("number"),
                "Avg HR": _empty_prop("number"),
                "Max HR": _empty_prop("number"),
                "Calories (kcal)": _empty_prop("number"),
                "Distance (km)": _empty_prop("number"),
                "Duration (min)": _empty_prop("number"),
                "Elevation Ascended (m)": _empty_prop("number"),
                "Elevation Descended (m)": _empty_prop("number"),
                "Intensity (kcal/hr/kg)": _empty_prop("number"),
                "Step Cadence (count/min)": _empty_prop("number"),
                "Steps": _empty_prop("number"),
                "Workout": _empty_prop("relation"),
            },
        }
        session = extract_session(page)

        assert session.name == "Minimal Session"
        assert session.source is None
        assert session.avg_hr is None
        assert session.workout_notion_id is None

    def test_relation_and_type_aliases_supported(self) -> None:
        page: dict[str, Any] = {
            **_SESSION_PAGE,
            "properties": {
                **_SESSION_PAGE["properties"],
                "Type": _select_prop("Running"),
                "Workouts": _relation_prop("workout-page-id"),
            },
        }

        # Remove canonical keys so alias resolution is actually exercised.
        page["properties"].pop("Session Type", None)
        page["properties"].pop("Workout", None)

        session = extract_session(page)

        assert session.session_type == "Running"
        assert session.workout_notion_id == "workout-page-id"

    def test_missing_name_raises_extraction_error(self) -> None:
        page: dict[str, Any] = {**_SESSION_PAGE, "properties": {"Name": _empty_prop("title")}}
        with pytest.raises(NotionExtractionError, match="missing required 'Name'"):
            extract_session(page)

    def test_date_parsed_from_datetime_string(self) -> None:
        session = extract_session(_SESSION_PAGE)
        assert session.start_start == datetime(2024, 2, 5, 6, 0, tzinfo=UTC)

    def test_missing_id_key_raises_extraction_error(self) -> None:
        page = {k: v for k, v in _SESSION_PAGE.items() if k != "id"}
        with pytest.raises(NotionExtractionError):
            extract_session(page)


# ===========================================================================
# extract_weekly_feedback
# ===========================================================================


class TestExtractWeeklyFeedback:
    def test_full_payload_extracts_correctly(self) -> None:
        feedback = extract_weekly_feedback(_FEEDBACK_PAGE)

        assert feedback.notion_id == "feedback-page-id"
        assert feedback.week == "Week 3"
        assert feedback.energy == 7.0
        assert feedback.leg_freshness == 6.0
        assert feedback.motivation == 8.0
        assert feedback.recovery == 7.5
        assert feedback.biggest_limitation == "Sleep"
        assert feedback.phase_notion_id == "phase-page-id"
        assert feedback.archived is False
        assert feedback.url == "https://www.notion.so/feedback-page-id"

    def test_optional_fields_absent(self) -> None:
        page: dict[str, Any] = {
            **_FEEDBACK_PAGE,
            "properties": {
                "Week": _title_prop("Week 4"),
                "Energy": _empty_prop("number"),
                "Leg Freshness": _empty_prop("number"),
                "Motivation": _empty_prop("number"),
                "Recovery": _empty_prop("number"),
                "Biggest Limitation": _empty_prop("select"),
                "Phase": _empty_prop("relation"),
            },
        }
        feedback = extract_weekly_feedback(page)

        assert feedback.week == "Week 4"
        assert feedback.energy is None
        assert feedback.leg_freshness is None
        assert feedback.motivation is None
        assert feedback.recovery is None
        assert feedback.biggest_limitation is None
        assert feedback.phase_notion_id is None

    def test_missing_week_raises_extraction_error(self) -> None:
        page: dict[str, Any] = {**_FEEDBACK_PAGE, "properties": {"Week": _empty_prop("title")}}
        with pytest.raises(NotionExtractionError, match="missing required 'Week'"):
            extract_weekly_feedback(page)

    def test_missing_id_key_raises_extraction_error(self) -> None:
        page = {k: v for k, v in _FEEDBACK_PAGE.items() if k != "id"}
        with pytest.raises(NotionExtractionError):
            extract_weekly_feedback(page)

    def test_archived_page_propagated(self) -> None:
        page = {**_FEEDBACK_PAGE, "archived": True}
        feedback = extract_weekly_feedback(page)
        assert feedback.archived is True

    def test_created_time_parsed(self) -> None:
        feedback = extract_weekly_feedback(_FEEDBACK_PAGE)
        assert feedback.created_time == datetime(2024, 2, 12, 20, 0, tzinfo=UTC)

    def test_last_edited_time_parsed(self) -> None:
        feedback = extract_weekly_feedback(_FEEDBACK_PAGE)
        assert feedback.last_edited_time == datetime(2024, 2, 12, 20, 5, tzinfo=UTC)


# ===========================================================================
# extract_nutrition_guideline
# ===========================================================================


class TestExtractNutritionGuideline:
    def test_full_payload_extracts_correctly(self) -> None:
        guideline = extract_nutrition_guideline(_NUTRITION_PAGE)

        assert guideline.notion_id == "nutrition-page-id"
        assert guideline.name == "Performance Fueling"
        assert guideline.goal == "Performance"
        assert guideline.applies_to == ["Endurance", "Hybrid"]
        assert guideline.carb_strategy == "Fuel hard sessions aggressively"
        assert guideline.protein_target_g_per_kg == "1.8"
        assert guideline.fat_target_g_per_kg == "0.8"
        assert guideline.hydration_electrolytes == "500-750ml/hr with sodium"
        assert guideline.supplements == "Creatine, caffeine"
        assert guideline.timing_rules == "Carbs before and during key sessions"
        assert guideline.created_time == datetime(2024, 1, 10, 8, 0, tzinfo=UTC)

    def test_optional_fields_absent(self) -> None:
        page: dict[str, Any] = {
            **_NUTRITION_PAGE,
            "properties": {
                "Name": _title_prop("Minimal Guideline"),
                "Goal": _empty_prop("select"),
                "Applies to": _empty_prop("multi_select"),
                "Carb strategy": _empty_prop("rich_text"),
                "Protein target (g/kg)": _empty_prop("rich_text"),
                "Fat target (g/kg)": _empty_prop("rich_text"),
                "Hydration / electrolytes": _empty_prop("rich_text"),
                "Supplements": _empty_prop("rich_text"),
                "Timing rules": _empty_prop("rich_text"),
            },
        }

        guideline = extract_nutrition_guideline(page)

        assert guideline.goal is None
        assert guideline.applies_to == []
        assert guideline.carb_strategy is None
        assert guideline.hydration_electrolytes is None

    def test_missing_name_raises_extraction_error(self) -> None:
        page: dict[str, Any] = {**_NUTRITION_PAGE, "properties": {"Name": _empty_prop("title")}}
        with pytest.raises(NotionExtractionError, match="missing required 'Name'"):
            extract_nutrition_guideline(page)
