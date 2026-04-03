"""Unit tests for the Notion extraction layer."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from ldk_athlete_ai_coach.core.integrations.notion.extractors import NotionExtractionError
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


def _checkbox_prop(value: bool) -> dict[str, Any]:
    return {"type": "checkbox", "checkbox": value}


def _date_prop(start: str, end: str | None = None) -> dict[str, Any]:
    return {"type": "date", "date": {"start": start, "end": end}}


def _relation_prop(*page_ids: str) -> dict[str, Any]:
    return {"type": "relation", "relation": [{"id": pid} for pid in page_ids]}


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
        "Phase Type": _select_prop("Base"),
        "Focus Tags": _multi_select_prop("Endurance", "Aerobic"),
        "Weekly Structure": _rich_text_prop("Mon: Run, Wed: Bike, Fri: Run"),
        "Timeframe": _date_prop("2024-02-01", "2024-03-15"),
        "Plan": _relation_prop("plan-page-id"),
        "Nutrition Guideline": _relation_prop("nutrition-page-id"),
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
        "Date": _date_prop("2024-02-05"),
        "Category": _select_prop("Run"),
        "Difficulty": _select_prop("Moderate"),
        "Equipment": _multi_select_prop("Shoes", "HR Monitor"),
        "Impact": _select_prop("High"),
        "Metrics to Record": _multi_select_prop("HR", "Pace"),
        "Purpose": _multi_select_prop("Aerobic Capacity"),
        "Primarily Used Muscle Group": _multi_select_prop("Legs"),
        "Planned Distance (km)": _number_prop(20.0),
        "Planned Duration (min)": _number_prop(110.0),
        "Planned RPE": _number_prop(6.0),
        "Planned Week Number": _number_prop(3.0),
        "Actual RPE": _number_prop(7.0),
        "Additional Info": _rich_text_prop("Easy pace throughout"),
        "Cancelled": _checkbox_prop(False),
        "Skipped": _checkbox_prop(False),
        "Phase": _relation_prop("phase-page-id"),
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
                "Phase Type": _empty_prop("select"),
                "Focus Tags": _empty_prop("multi_select"),
                "Weekly Structure": _empty_prop("rich_text"),
                "Timeframe": _empty_prop("date"),
                "Plan": _empty_prop("relation"),
                "Nutrition Guideline": _empty_prop("relation"),
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
        assert workout.difficulty == "Moderate"
        assert workout.equipment == ["Shoes", "HR Monitor"]
        assert workout.impact == "High"
        assert workout.metrics_to_record == ["HR", "Pace"]
        assert workout.purpose == ["Aerobic Capacity"]
        assert workout.primarily_used_muscle_group == ["Legs"]
        assert workout.planned_distance_km == 20.0
        assert workout.planned_duration_min == 110.0
        assert workout.planned_rpe == 6.0
        assert workout.planned_week_number == 3.0
        assert workout.actual_rpe == 7.0
        assert workout.additional_info == "Easy pace throughout"
        assert workout.cancelled is False
        assert workout.skipped is False
        assert workout.phase_notion_id == "phase-page-id"
        assert workout.url == "https://www.notion.so/workout-page-id"

    def test_optional_fields_absent(self) -> None:
        page: dict[str, Any] = {
            **_WORKOUT_PAGE,
            "properties": {
                "Name": _title_prop("Minimal Workout"),
                "Date": _empty_prop("date"),
                "Category": _empty_prop("select"),
                "Difficulty": _empty_prop("select"),
                "Equipment": _empty_prop("multi_select"),
                "Impact": _empty_prop("select"),
                "Metrics to Record": _empty_prop("multi_select"),
                "Purpose": _empty_prop("multi_select"),
                "Primarily Used Muscle Group": _empty_prop("multi_select"),
                "Planned Distance (km)": _empty_prop("number"),
                "Planned Duration (min)": _empty_prop("number"),
                "Planned RPE": _empty_prop("number"),
                "Planned Week Number": _empty_prop("number"),
                "Actual RPE": _empty_prop("number"),
                "Additional Info": _empty_prop("rich_text"),
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
        assert workout.cancelled is False
        assert workout.phase_notion_id is None

    def test_missing_name_raises_extraction_error(self) -> None:
        page: dict[str, Any] = {**_WORKOUT_PAGE, "properties": {"Name": _empty_prop("title")}}
        with pytest.raises(NotionExtractionError, match="missing required 'Name'"):
            extract_workout(page)

    def test_date_with_range_and_datetime_flag(self) -> None:
        page: dict[str, Any] = {
            **_WORKOUT_PAGE,
            "properties": {
                **_WORKOUT_PAGE["properties"],
                "Date": _date_prop("2024-02-05T07:00:00+00:00", "2024-02-05T09:00:00+00:00"),
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
