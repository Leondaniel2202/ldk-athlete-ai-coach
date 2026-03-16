"""Tests for the Notion sync layer (transformers + service)."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, call, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import ldk_athlete_ai_coach.db.models  # noqa: F401 – registers all models
from ldk_athlete_ai_coach.db.base import Base
from ldk_athlete_ai_coach.db.models.sport_manager import (
    Event,
    Feedback,
    NutritionGuideline,
    Phase,
    Plan,
    TrackedSession,
    TrainingLoad,
    Workout,
)
from ldk_athlete_ai_coach.notion_sync import NotionClient, NotionSyncService
from ldk_athlete_ai_coach.notion_sync import transformers as T

# ---------------------------------------------------------------------------
# Shared Notion page fixtures
# ---------------------------------------------------------------------------

PLAN_PAGE: dict = {
    "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "url": "https://notion.so/plan-page",
    "properties": {
        "Name": {"title": [{"plain_text": "My Plan"}]},
        "Goal": {"rich_text": [{"plain_text": "Finish sub-3 marathon"}]},
        "Constraints": {"rich_text": [{"plain_text": "No morning workouts"}]},
        "Weekly Rhythm": {"rich_text": [{"plain_text": "Mon-Fri"}]},
        "Start Date": {"date": {"start": "2026-01-01", "end": None}},
        "End Date": {"date": {"start": "2026-06-30", "end": None}},
    },
}

NUTRITION_PAGE: dict = {
    "id": "11111111-2222-3333-4444-555555555555",
    "url": "https://notion.so/nutrition-page",
    "properties": {
        "Name": {"title": [{"plain_text": "High Carb"}]},
        "Goal": {"select": {"name": "Performance"}},
        "Applies To": {"multi_select": [{"name": "Race Day"}, {"name": "Long Run"}]},
        "Carb Strategy": {"rich_text": [{"plain_text": "Load 3 days before"}]},
        "Protein Target (g/kg)": {"rich_text": [{"plain_text": "1.6"}]},
        "Fat Target (g/kg)": {"rich_text": [{"plain_text": "1.0"}]},
        "Hydration & Electrolytes": {"rich_text": [{"plain_text": "750ml/hr"}]},
        "Supplements": {"rich_text": [{"plain_text": "Caffeine"}]},
        "Timing Rules": {"rich_text": [{"plain_text": "Eat 2h before"}]},
    },
}

TRAINING_LOAD_PAGE: dict = {
    "id": "aaaaaaaa-0000-0000-0000-000000000001",
    "url": "https://notion.so/tl-page",
    "properties": {
        "Name": {"title": [{"plain_text": "Easy"}]},
        "Impact": {"select": {"name": "Low"}},
        "Min Load": {"number": 0},
        "Max Load": {"number": 50},
        "Typical Avg RPE": {"number": 3.0},
        "Meaning": {"rich_text": [{"plain_text": "Recovery session"}]},
    },
}

PHASE_PAGE: dict = {
    "id": "cccccccc-dddd-eeee-ffff-000000000000",
    "url": "https://notion.so/phase-page",
    "properties": {
        "Name": {"title": [{"plain_text": "Base Phase"}]},
        "Notes": {"rich_text": [{"plain_text": "Build aerobic base"}]},
        "Phase Type": {"select": {"name": "Base"}},
        "Focus Tags": {"multi_select": [{"name": "Endurance"}, {"name": "Zone 2"}]},
        "Weekly Structure": {"rich_text": [{"plain_text": "3 easy, 1 long"}]},
        "Timeframe": {
            "date": {
                "start": "2026-01-01T06:00:00+00:00",
                "end": "2026-03-31T06:00:00+00:00",
            }
        },
        "Plan": {"relation": [{"id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"}]},
        "Nutrition Guideline": {"relation": [{"id": "11111111-2222-3333-4444-555555555555"}]},
    },
}

WORKOUT_PAGE: dict = {
    "id": "wwwwwwww-0000-0000-0000-000000000001",
    "url": "https://notion.so/workout-page",
    "properties": {
        "Name": {"title": [{"plain_text": "Easy 10K"}]},
        "Date": {"date": {"start": "2026-01-05", "end": None}},
        "Category": {"select": {"name": "Run"}},
        "Difficulty": {"select": {"name": "Easy"}},
        "Equipment": {"multi_select": [{"name": "Shoes"}]},
        "Impact": {"select": {"name": "Low"}},
        "Metrics to Record": {"multi_select": [{"name": "HR"}, {"name": "Pace"}]},
        "Purpose": {"multi_select": [{"name": "Aerobic base"}]},
        "Primarily Used Muscle Group": {"multi_select": [{"name": "Legs"}]},
        "Planned Distance (km)": {"number": 10.0},
        "Planned Duration (min)": {"number": 55.0},
        "Planned RPE": {"number": 4.0},
        "Planned Week Number": {"number": 1.0},
        "Actual RPE": {"number": None},
        "Additional Info": {"rich_text": []},
        "Cancelled": {"checkbox": False},
        "Skipped": {"checkbox": False},
        "Phase": {"relation": [{"id": "cccccccc-dddd-eeee-ffff-000000000000"}]},
    },
}

EVENT_PAGE: dict = {
    "id": "evevevev-0000-0000-0000-000000000001",
    "url": "https://notion.so/event-page",
    "properties": {
        "Name": {"title": [{"plain_text": "Spring Marathon"}]},
        "Type": {"select": {"name": "Race"}},
        "Target": {"rich_text": [{"plain_text": "Sub 3h"}]},
        "Format": {"rich_text": [{"plain_text": "Road"}]},
        "Notes": {"rich_text": []},
        "Priority": {"select": {"name": "A"}},
        "Start Date": {"date": {"start": "2026-04-19", "end": None}},
        "End Date": {"date": {"start": "2026-04-19", "end": None}},
        "Place Name": {"rich_text": [{"plain_text": "Vienna"}]},
        "Place Address": {"rich_text": []},
        "Latitude": {"number": 48.2082},
        "Longitude": {"number": 16.3738},
        "Google Place ID": {"rich_text": []},
        "Plan": {"relation": [{"id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"}]},
        "Race Workout": {"relation": [{"id": "wwwwwwww-0000-0000-0000-000000000001"}]},
    },
}

TRACKED_SESSION_PAGE: dict = {
    "id": "tstsidid-0000-0000-0000-000000000001",
    "url": "https://notion.so/ts-page",
    "properties": {
        "Name": {"title": [{"plain_text": "Morning Run"}]},
        "Source": {"select": {"name": "Apple Health"}},
        "Session Type": {"rich_text": [{"plain_text": "Running"}]},
        "External ID": {"rich_text": [{"plain_text": "abc123"}]},
        "Start": {"date": {"start": "2026-01-05T06:00:00+00:00", "end": None}},
        "End": {"date": {"start": "2026-01-05T06:55:00+00:00", "end": None}},
        "Active Energy (kJ)": {"number": 1200.0},
        "Active Energy Burned (kJ)": {"number": 1100.0},
        "Avg HR": {"number": 145.0},
        "Max HR": {"number": 162.0},
        "Calories (kcal)": {"number": 520.0},
        "Distance (km)": {"number": 10.1},
        "Duration (min)": {"number": 55.5},
        "Elevation Ascended (m)": {"number": 45.0},
        "Elevation Descended (m)": {"number": 42.0},
        "Intensity (kcal/hr/kg)": {"number": 8.5},
        "Step Cadence (count/min)": {"number": 170.0},
        "Steps": {"number": 9400.0},
        "Workout": {"relation": [{"id": "wwwwwwww-0000-0000-0000-000000000001"}]},
    },
}

FEEDBACK_PAGE: dict = {
    "id": "fbfbfbfb-0000-0000-0000-000000000001",
    "url": "https://notion.so/feedback-page",
    "properties": {
        "Week": {"title": [{"plain_text": "Week 1"}]},
        "Energy": {"number": 7.0},
        "Leg Freshness": {"number": 8.0},
        "Motivation": {"number": 9.0},
        "Recovery": {"number": 7.5},
        "Biggest Limitation": {"select": {"name": "Sleep"}},
        "Phase": {"relation": [{"id": "cccccccc-dddd-eeee-ffff-000000000000"}]},
    },
}


# ---------------------------------------------------------------------------
# Transformer unit tests
# ---------------------------------------------------------------------------


class TestTransformPlan:
    def test_extracts_all_core_fields(self) -> None:
        result = T.transform_plan(PLAN_PAGE)

        assert result["notion_page_id"] == "aaaaaaaabbbbccccddddeeeeeeeeeeee"
        assert result["notion_url"] == "https://notion.so/plan-page"
        assert result["name"] == "My Plan"
        assert result["plan_goal"] == "Finish sub-3 marathon"
        assert result["constraints"] == "No morning workouts"
        assert result["rules_weekly_rhythm"] == "Mon-Fri"

    def test_parses_date_start_only(self) -> None:
        result = T.transform_plan(PLAN_PAGE)

        assert result["start_date_start"] == datetime(2026, 1, 1, tzinfo=UTC)
        assert result["start_date_end"] is None
        assert result["start_date_is_datetime"] is False

    def test_parses_end_date(self) -> None:
        result = T.transform_plan(PLAN_PAGE)

        assert result["end_date_start"] == datetime(2026, 6, 30, tzinfo=UTC)
        assert result["end_date_is_datetime"] is False

    def test_empty_optional_fields_return_none(self) -> None:
        page: dict = {
            "id": "00000000-0000-0000-0000-000000000000",
            "url": "https://notion.so/empty",
            "properties": {"Name": {"title": [{"plain_text": "Minimal"}]}},
        }
        result = T.transform_plan(page)

        assert result["plan_goal"] is None
        assert result["constraints"] is None
        assert result["start_date_start"] is None
        assert result["end_date_start"] is None


class TestTransformNutritionGuideline:
    def test_extracts_all_fields(self) -> None:
        result = T.transform_nutrition_guideline(NUTRITION_PAGE)

        assert result["notion_page_id"] == "11111111222233334444555555555555"
        assert result["name"] == "High Carb"
        assert result["goal"] == "Performance"
        assert result["applies_to"] == ["Race Day", "Long Run"]
        assert result["carb_strategy"] == "Load 3 days before"
        assert result["protein_target_g_per_kg"] == "1.6"
        assert result["fat_target_g_per_kg"] == "1.0"

    def test_empty_multi_select_returns_empty_list(self) -> None:
        page: dict = {
            "id": "00000000-0000-0000-0000-000000000099",
            "url": "https://notion.so/empty",
            "properties": {"Name": {"title": [{"plain_text": "Base"}]}},
        }
        result = T.transform_nutrition_guideline(page)

        assert result["applies_to"] == []


class TestTransformTrainingLoad:
    def test_extracts_numeric_fields(self) -> None:
        result = T.transform_training_load(TRAINING_LOAD_PAGE)

        assert result["name"] == "Easy"
        assert result["impact"] == "Low"
        assert result["min_load"] == 0
        assert result["max_load"] == 50
        assert result["typical_avg_rpe"] == 3.0
        assert result["meaning"] == "Recovery session"


class TestTransformPhase:
    def test_extracts_fields_and_relation_stubs(self) -> None:
        result = T.transform_phase(PHASE_PAGE)

        assert result["name"] == "Base Phase"
        assert result["phase_type"] == "Base"
        assert result["focus_tags"] == ["Endurance", "Zone 2"]
        assert result["timeframe_is_datetime"] is True
        assert result["plan_notion_id"] == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        assert result["nutrition_notion_id"] == "11111111-2222-3333-4444-555555555555"

    def test_datetime_flag_for_datetime_value(self) -> None:
        result = T.transform_phase(PHASE_PAGE)

        assert result["timeframe_is_datetime"] is True
        assert isinstance(result["timeframe_start"], datetime)


class TestTransformWorkout:
    def test_extracts_metrics_and_flags(self) -> None:
        result = T.transform_workout(WORKOUT_PAGE)

        assert result["name"] == "Easy 10K"
        assert result["category"] == "Run"
        assert result["planned_distance_km"] == 10.0
        assert result["planned_duration_min"] == 55.0
        assert result["cancelled"] is False
        assert result["skipped"] is False
        assert result["equipment"] == ["Shoes"]
        assert "HR" in result["metrics_to_record"]

    def test_phase_relation_stub_present(self) -> None:
        result = T.transform_workout(WORKOUT_PAGE)

        assert result["phase_notion_id"] == "cccccccc-dddd-eeee-ffff-000000000000"

    def test_date_only_produces_no_is_datetime(self) -> None:
        result = T.transform_workout(WORKOUT_PAGE)

        assert result["date_is_datetime"] is False


class TestTransformEvent:
    def test_extracts_location_and_priority(self) -> None:
        result = T.transform_event(EVENT_PAGE)

        assert result["name"] == "Spring Marathon"
        assert result["event_type"] == "Race"
        assert result["priority"] == "A"
        assert result["place_name"] == "Vienna"
        assert result["place_latitude"] == 48.2082
        assert result["place_longitude"] == 16.3738

    def test_relation_stubs_present(self) -> None:
        result = T.transform_event(EVENT_PAGE)

        assert result["plan_notion_id"] == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        assert result["race_workout_notion_id"] == "wwwwwwww-0000-0000-0000-000000000001"


class TestTransformTrackedSession:
    def test_extracts_performance_metrics(self) -> None:
        result = T.transform_tracked_session(TRACKED_SESSION_PAGE)

        assert result["name"] == "Morning Run"
        assert result["source"] == "Apple Health"
        assert result["avg_hr"] == 145.0
        assert result["distance_km"] == 10.1
        assert result["steps"] == 9400.0

    def test_workout_relation_stub_present(self) -> None:
        result = T.transform_tracked_session(TRACKED_SESSION_PAGE)

        assert result["workout_notion_id"] == "wwwwwwww-0000-0000-0000-000000000001"


class TestTransformFeedback:
    def test_extracts_scores(self) -> None:
        result = T.transform_feedback(FEEDBACK_PAGE)

        assert result["week"] == "Week 1"
        assert result["energy"] == 7.0
        assert result["motivation"] == 9.0
        assert result["biggest_limitation"] == "Sleep"

    def test_phase_relation_stub_present(self) -> None:
        result = T.transform_feedback(FEEDBACK_PAGE)

        assert result["phase_notion_id"] == "cccccccc-dddd-eeee-ffff-000000000000"


# ---------------------------------------------------------------------------
# Helpers tests
# ---------------------------------------------------------------------------


class TestDateParsing:
    def test_date_only_parses_to_midnight_utc(self) -> None:
        prop = {"date": {"start": "2026-03-15", "end": None}}
        result = T._date_start(prop)

        assert result == datetime(2026, 3, 15, tzinfo=UTC)

    def test_datetime_parses_and_preserves_timezone(self) -> None:
        prop = {"date": {"start": "2026-03-15T08:00:00+00:00", "end": None}}
        result = T._date_start(prop)

        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    def test_missing_date_returns_none(self) -> None:
        assert T._date_start({}) is None
        assert T._date_end({}) is None

    def test_date_flag_false_for_date_only(self) -> None:
        prop = {"date": {"start": "2026-01-01", "end": None}}
        assert T._date_is_datetime(prop) is False

    def test_date_flag_true_for_datetime(self) -> None:
        prop = {"date": {"start": "2026-01-01T00:00:00+00:00", "end": None}}
        assert T._date_is_datetime(prop) is True


class TestPageId:
    def test_removes_hyphens_from_uuid(self) -> None:
        page = {"id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", "url": ""}
        assert T._page_id(page) == "aaaaaaaabbbbccccddddeeeeeeeeeeee"


# ---------------------------------------------------------------------------
# Service integration tests (in-memory SQLite)
# ---------------------------------------------------------------------------


@pytest.fixture()
def in_memory_db_session() -> Session:
    """Provide a transient in-memory SQLite session for service tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionFactory = sessionmaker(bind=engine)
    session = SessionFactory()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def _mock_client(pages_by_db: dict) -> MagicMock:
    """Build a mock NotionClient whose query_database returns from *pages_by_db*."""
    mock = MagicMock(spec=NotionClient)
    mock.query_database.side_effect = lambda db_id: pages_by_db.get(db_id, [])
    return mock


class TestNotionSyncServicePlans:
    def test_inserts_new_plan(self, in_memory_db_session: Session) -> None:
        client = _mock_client({"db_plans": [PLAN_PAGE]})
        service = NotionSyncService(client, in_memory_db_session, db_plans="db_plans")

        id_map = service.sync_plans()
        in_memory_db_session.commit()

        assert len(id_map) == 1
        plan = in_memory_db_session.query(Plan).one()
        assert plan.name == "My Plan"
        assert plan.plan_goal == "Finish sub-3 marathon"
        assert plan.notion_page_id == "aaaaaaaabbbbccccddddeeeeeeeeeeee"

    def test_updates_existing_plan(self, in_memory_db_session: Session) -> None:
        client = _mock_client({"db_plans": [PLAN_PAGE]})
        service = NotionSyncService(client, in_memory_db_session, db_plans="db_plans")

        # First sync – creates the row
        service.sync_plans()
        in_memory_db_session.commit()

        # Modify the in-memory page and sync again
        updated_page = {
            **PLAN_PAGE,
            "properties": {
                **PLAN_PAGE["properties"],
                "Goal": {"rich_text": [{"plain_text": "Sub 2:50 marathon"}]},
            },
        }
        client2 = _mock_client({"db_plans": [updated_page]})
        service2 = NotionSyncService(client2, in_memory_db_session, db_plans="db_plans")
        service2.sync_plans()
        in_memory_db_session.commit()

        plans = in_memory_db_session.query(Plan).all()
        assert len(plans) == 1  # no duplicate
        assert plans[0].plan_goal == "Sub 2:50 marathon"

    def test_skips_when_no_db_configured(self, in_memory_db_session: Session) -> None:
        client = _mock_client({})
        service = NotionSyncService(client, in_memory_db_session)

        result = service.sync_plans()

        assert result == {}
        client.query_database.assert_not_called()


class TestNotionSyncServicePhases:
    def test_resolves_plan_fk(self, in_memory_db_session: Session) -> None:
        client = _mock_client(
            {
                "db_plans": [PLAN_PAGE],
                "db_phases": [PHASE_PAGE],
            }
        )
        service = NotionSyncService(
            client, in_memory_db_session, db_plans="db_plans", db_phases="db_phases"
        )

        plan_ids = service.sync_plans()
        in_memory_db_session.commit()
        service.sync_phases(plan_ids=plan_ids)
        in_memory_db_session.commit()

        phase = in_memory_db_session.query(Phase).one()
        plan = in_memory_db_session.query(Plan).one()
        assert phase.plan_id == plan.id


class TestNotionSyncServiceWorkouts:
    def test_resolves_phase_fk(self, in_memory_db_session: Session) -> None:
        client = _mock_client(
            {
                "db_plans": [PLAN_PAGE],
                "db_phases": [PHASE_PAGE],
                "db_workouts": [WORKOUT_PAGE],
            }
        )
        service = NotionSyncService(
            client,
            in_memory_db_session,
            db_plans="db_plans",
            db_phases="db_phases",
            db_workouts="db_workouts",
        )

        plan_ids = service.sync_plans()
        in_memory_db_session.commit()
        phase_ids = service.sync_phases(plan_ids=plan_ids)
        in_memory_db_session.commit()
        service.sync_workouts(phase_ids=phase_ids)
        in_memory_db_session.commit()

        workout = in_memory_db_session.query(Workout).one()
        phase = in_memory_db_session.query(Phase).one()
        assert workout.phase_id == phase.id


class TestNotionSyncServiceSyncAll:
    def test_syncs_all_entities_in_order(self, in_memory_db_session: Session) -> None:
        client = _mock_client(
            {
                "db_plans": [PLAN_PAGE],
                "db_nutrition": [NUTRITION_PAGE],
                "db_tl": [TRAINING_LOAD_PAGE],
                "db_phases": [PHASE_PAGE],
                "db_workouts": [WORKOUT_PAGE],
                "db_events": [EVENT_PAGE],
                "db_ts": [TRACKED_SESSION_PAGE],
                "db_feedback": [FEEDBACK_PAGE],
            }
        )
        service = NotionSyncService(
            client,
            in_memory_db_session,
            db_plans="db_plans",
            db_nutrition_guidelines="db_nutrition",
            db_training_loads="db_tl",
            db_phases="db_phases",
            db_workouts="db_workouts",
            db_events="db_events",
            db_tracked_sessions="db_ts",
            db_feedback="db_feedback",
        )

        service.sync_all()

        assert in_memory_db_session.query(Plan).count() == 1
        assert in_memory_db_session.query(NutritionGuideline).count() == 1
        assert in_memory_db_session.query(TrainingLoad).count() == 1
        assert in_memory_db_session.query(Phase).count() == 1
        assert in_memory_db_session.query(Workout).count() == 1
        assert in_memory_db_session.query(Event).count() == 1
        assert in_memory_db_session.query(TrackedSession).count() == 1
        assert in_memory_db_session.query(Feedback).count() == 1

    def test_partial_config_only_syncs_configured_dbs(self, in_memory_db_session: Session) -> None:
        client = _mock_client({"db_plans": [PLAN_PAGE]})
        service = NotionSyncService(client, in_memory_db_session, db_plans="db_plans")

        service.sync_all()

        assert in_memory_db_session.query(Plan).count() == 1
        # No other entity should have been synced
        assert in_memory_db_session.query(Phase).count() == 0
        assert in_memory_db_session.query(Workout).count() == 0


class TestNotionSyncServiceFeedback:
    def test_resolves_phase_fk(self, in_memory_db_session: Session) -> None:
        client = _mock_client(
            {
                "db_plans": [PLAN_PAGE],
                "db_phases": [PHASE_PAGE],
                "db_feedback": [FEEDBACK_PAGE],
            }
        )
        service = NotionSyncService(
            client,
            in_memory_db_session,
            db_plans="db_plans",
            db_phases="db_phases",
            db_feedback="db_feedback",
        )

        plan_ids = service.sync_plans()
        in_memory_db_session.commit()
        phase_ids = service.sync_phases(plan_ids=plan_ids)
        in_memory_db_session.commit()
        service.sync_feedback(phase_ids=phase_ids)
        in_memory_db_session.commit()

        fb = in_memory_db_session.query(Feedback).one()
        phase = in_memory_db_session.query(Phase).one()
        assert fb.phase_id == phase.id


# ---------------------------------------------------------------------------
# NotionClient unit test (mocked SDK)
# ---------------------------------------------------------------------------


class TestNotionClient:
    def test_query_database_follows_pagination(self) -> None:
        """NotionClient.query_database should follow cursor pagination."""
        mock_sdk = MagicMock()
        mock_sdk.databases.query.side_effect = [
            {"results": [{"id": "page1"}], "has_more": True, "next_cursor": "cur1"},
            {"results": [{"id": "page2"}], "has_more": False, "next_cursor": None},
        ]

        with patch("ldk_athlete_ai_coach.notion_sync.client.Client", return_value=mock_sdk):
            client = NotionClient(auth="secret_test")
            pages = client.query_database("db-id")

        assert pages == [{"id": "page1"}, {"id": "page2"}]
        assert mock_sdk.databases.query.call_count == 2
        # Second call should include the cursor
        second_call = mock_sdk.databases.query.call_args_list[1]
        assert second_call == call(database_id="db-id", start_cursor="cur1")

    def test_query_database_single_page(self) -> None:
        mock_sdk = MagicMock()
        mock_sdk.databases.query.return_value = {
            "results": [{"id": "only-page"}],
            "has_more": False,
        }

        with patch("ldk_athlete_ai_coach.notion_sync.client.Client", return_value=mock_sdk):
            client = NotionClient(auth="secret_test")
            pages = client.query_database("db-id")

        assert len(pages) == 1
        mock_sdk.databases.query.assert_called_once_with(database_id="db-id")
