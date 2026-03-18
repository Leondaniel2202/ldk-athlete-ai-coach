"""Unit tests for the Notion sync service."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from ldk_athlete_ai_coach.core.config import Settings
from ldk_athlete_ai_coach.core.integrations.notion.client import NotionClient
from ldk_athlete_ai_coach.core.integrations.notion.extractors import NotionExtractionError
from ldk_athlete_ai_coach.core.integrations.notion.sync_service import (
    NotionSyncService,
    SyncResult,
)
from ldk_athlete_ai_coach.db.models.sport_manager import Feedback, Phase, TrackedSession, Workout

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _settings(**overrides: Any) -> Settings:
    """Return a minimal :class:`Settings` instance with all required fields populated."""
    defaults: dict[str, Any] = {
        "postgres_db": "test_db",
        "postgres_user": "postgres",
        "postgres_password": "postgres",
        "postgres_host": "localhost",
        "postgres_port": 5432,
        "notion_api_key": "secret_test_key",
        "notion_phase_db_id": "phase-db-id",
        "notion_workout_db_id": "workout-db-id",
        "notion_session_db_id": "session-db-id",
        "notion_feedback_db_id": "feedback-db-id",
        "notion_page_size": 100,
        "notion_timeout_seconds": 30,
        "notion_max_retries": 3,
    }
    defaults.update(overrides)
    return Settings(**defaults)  # pyright: ignore[reportCallIssue]


def _make_service(raw_pages_by_db: dict[str, list[dict[str, Any]]]) -> NotionSyncService:
    """Return a :class:`NotionSyncService` whose client returns controlled raw pages.

    Args:
        raw_pages_by_db: Maps database_id to the list of raw pages the client
            should return when that database is queried.
    """
    settings = _settings()
    client = MagicMock(spec=NotionClient)

    def _iter(database_id: str) -> list[dict[str, Any]]:
        return iter(raw_pages_by_db.get(database_id, []))

    client.iter_database_entries.side_effect = _iter
    return NotionSyncService(client, settings)


_DT = datetime(2024, 3, 1, 8, 0, 0, tzinfo=UTC)
_DT2 = datetime(2024, 6, 30, 20, 0, 0, tzinfo=UTC)
_TS = "2024-03-01T08:00:00.000Z"


# ---------------------------------------------------------------------------
# Minimal raw-page factory helpers
# ---------------------------------------------------------------------------


def _title_prop(text: str) -> dict[str, Any]:
    return {"type": "title", "title": [{"plain_text": text}]}


def _rich_text_prop(text: str) -> dict[str, Any]:
    return {"type": "rich_text", "rich_text": [{"plain_text": text}]}


def _select_prop(name: str) -> dict[str, Any]:
    return {"type": "select", "select": {"name": name}}


def _number_prop(value: float) -> dict[str, Any]:
    return {"type": "number", "number": value}


def _date_prop(start: str, end: str | None = None) -> dict[str, Any]:
    return {"type": "date", "date": {"start": start, "end": end}}


def _relation_prop(*page_ids: str) -> dict[str, Any]:
    return {"type": "relation", "relation": [{"id": pid} for pid in page_ids]}


def _raw_phase(
    notion_id: str = "phase-1",
    name: str = "Base Phase",
) -> dict[str, Any]:
    return {
        "id": notion_id,
        "url": f"https://notion.so/{notion_id}",
        "archived": False,
        "created_time": _TS,
        "last_edited_time": _TS,
        "properties": {
            "Name": _title_prop(name),
        },
    }


def _raw_workout(
    notion_id: str = "workout-1",
    name: str = "Long Run",
) -> dict[str, Any]:
    return {
        "id": notion_id,
        "url": f"https://notion.so/{notion_id}",
        "archived": False,
        "created_time": _TS,
        "last_edited_time": _TS,
        "properties": {
            "Name": _title_prop(name),
        },
    }


def _raw_session(
    notion_id: str = "session-1",
    name: str = "Morning Run",
) -> dict[str, Any]:
    return {
        "id": notion_id,
        "url": f"https://notion.so/{notion_id}",
        "archived": False,
        "created_time": _TS,
        "last_edited_time": _TS,
        "properties": {
            "Name": _title_prop(name),
        },
    }


def _raw_feedback(
    notion_id: str = "feedback-1",
    week: str = "2024-W10",
) -> dict[str, Any]:
    return {
        "id": notion_id,
        "url": f"https://notion.so/{notion_id}",
        "archived": False,
        "created_time": _TS,
        "last_edited_time": _TS,
        "properties": {
            "Week": _title_prop(week),
        },
    }


# ===========================================================================
# SyncResult
# ===========================================================================


class TestSyncResult:
    def test_defaults(self) -> None:
        result = SyncResult(entity="Phase")

        assert result.entity == "Phase"
        assert result.fetched == 0
        assert result.success == 0
        assert result.failed == 0
        assert result.entities == []

    def test_entities_list_is_independent(self) -> None:
        r1 = SyncResult(entity="A")
        r2 = SyncResult(entity="B")
        r1.entities.append("x")

        assert r2.entities == []

    def test_counts_can_be_incremented(self) -> None:
        result = SyncResult(entity="Phase", fetched=3, success=2, failed=1)

        assert result.fetched == 3
        assert result.success == 2
        assert result.failed == 1


# ===========================================================================
# sync_phases
# ===========================================================================


class TestSyncPhases:
    def test_returns_sync_result_for_phase(self) -> None:
        service = _make_service({"phase-db-id": [_raw_phase()]})
        result = service.sync_phases()

        assert isinstance(result, SyncResult)
        assert result.entity == "Phase"

    def test_fetches_from_correct_database(self) -> None:
        service = _make_service({"phase-db-id": [_raw_phase()]})
        result = service.sync_phases()

        assert result.fetched == 1

    def test_successful_extraction_increments_success(self) -> None:
        service = _make_service({"phase-db-id": [_raw_phase("p1"), _raw_phase("p2")]})
        result = service.sync_phases()

        assert result.fetched == 2
        assert result.success == 2
        assert result.failed == 0

    def test_entities_are_phase_instances(self) -> None:
        service = _make_service({"phase-db-id": [_raw_phase()]})
        result = service.sync_phases()

        assert len(result.entities) == 1
        assert isinstance(result.entities[0], Phase)

    def test_entity_notion_id_is_mapped(self) -> None:
        service = _make_service({"phase-db-id": [_raw_phase(notion_id="phase-xyz", name="Speed")]})
        result = service.sync_phases()

        entity = result.entities[0]
        assert isinstance(entity, Phase)
        assert entity.notion_page_id == "phase-xyz"
        assert entity.name == "Speed"

    def test_malformed_page_increments_failed(self) -> None:
        bad_page: dict[str, Any] = {"id": "bad-phase", "properties": {}}  # missing Name
        service = _make_service({"phase-db-id": [bad_page]})
        result = service.sync_phases()

        assert result.fetched == 1
        assert result.success == 0
        assert result.failed == 1
        assert result.entities == []

    def test_mixed_good_and_bad_pages(self) -> None:
        bad_page: dict[str, Any] = {"id": "bad", "properties": {}}
        service = _make_service({"phase-db-id": [_raw_phase("p1"), bad_page, _raw_phase("p2")]})
        result = service.sync_phases()

        assert result.fetched == 3
        assert result.success == 2
        assert result.failed == 1

    def test_empty_database_returns_zero_counts(self) -> None:
        service = _make_service({"phase-db-id": []})
        result = service.sync_phases()

        assert result.fetched == 0
        assert result.success == 0
        assert result.failed == 0
        assert result.entities == []


# ===========================================================================
# sync_workouts
# ===========================================================================


class TestSyncWorkouts:
    def test_returns_sync_result_for_workout(self) -> None:
        service = _make_service({"workout-db-id": [_raw_workout()]})
        result = service.sync_workouts()

        assert isinstance(result, SyncResult)
        assert result.entity == "Workout"

    def test_successful_extraction(self) -> None:
        service = _make_service({"workout-db-id": [_raw_workout("w1"), _raw_workout("w2")]})
        result = service.sync_workouts()

        assert result.fetched == 2
        assert result.success == 2
        assert result.failed == 0

    def test_entities_are_workout_instances(self) -> None:
        service = _make_service({"workout-db-id": [_raw_workout()]})
        result = service.sync_workouts()

        assert isinstance(result.entities[0], Workout)

    def test_entity_notion_id_is_mapped(self) -> None:
        service = _make_service(
            {"workout-db-id": [_raw_workout(notion_id="workout-abc", name="Intervals")]}
        )
        result = service.sync_workouts()

        entity = result.entities[0]
        assert isinstance(entity, Workout)
        assert entity.notion_page_id == "workout-abc"
        assert entity.name == "Intervals"

    def test_malformed_page_increments_failed(self) -> None:
        bad_page: dict[str, Any] = {"id": "bad-workout", "properties": {}}
        service = _make_service({"workout-db-id": [bad_page]})
        result = service.sync_workouts()

        assert result.failed == 1
        assert result.success == 0


# ===========================================================================
# sync_sessions
# ===========================================================================


class TestSyncSessions:
    def test_returns_sync_result_for_tracked_session(self) -> None:
        service = _make_service({"session-db-id": [_raw_session()]})
        result = service.sync_sessions()

        assert isinstance(result, SyncResult)
        assert result.entity == "TrackedSession"

    def test_successful_extraction(self) -> None:
        service = _make_service(
            {"session-db-id": [_raw_session("s1"), _raw_session("s2"), _raw_session("s3")]}
        )
        result = service.sync_sessions()

        assert result.fetched == 3
        assert result.success == 3
        assert result.failed == 0

    def test_entities_are_tracked_session_instances(self) -> None:
        service = _make_service({"session-db-id": [_raw_session()]})
        result = service.sync_sessions()

        assert isinstance(result.entities[0], TrackedSession)

    def test_entity_notion_id_is_mapped(self) -> None:
        service = _make_service(
            {"session-db-id": [_raw_session(notion_id="session-xyz", name="Evening Run")]}
        )
        result = service.sync_sessions()

        entity = result.entities[0]
        assert isinstance(entity, TrackedSession)
        assert entity.notion_page_id == "session-xyz"
        assert entity.name == "Evening Run"

    def test_malformed_page_increments_failed(self) -> None:
        bad_page: dict[str, Any] = {"id": "bad-session", "properties": {}}
        service = _make_service({"session-db-id": [bad_page]})
        result = service.sync_sessions()

        assert result.failed == 1
        assert result.success == 0


# ===========================================================================
# sync_weekly_feedback
# ===========================================================================


class TestSyncWeeklyFeedback:
    def test_returns_sync_result_for_feedback(self) -> None:
        service = _make_service({"feedback-db-id": [_raw_feedback()]})
        result = service.sync_weekly_feedback()

        assert isinstance(result, SyncResult)
        assert result.entity == "Feedback"

    def test_successful_extraction(self) -> None:
        service = _make_service(
            {"feedback-db-id": [_raw_feedback("f1", "2024-W10"), _raw_feedback("f2", "2024-W11")]}
        )
        result = service.sync_weekly_feedback()

        assert result.fetched == 2
        assert result.success == 2
        assert result.failed == 0

    def test_entities_are_feedback_instances(self) -> None:
        service = _make_service({"feedback-db-id": [_raw_feedback()]})
        result = service.sync_weekly_feedback()

        assert isinstance(result.entities[0], Feedback)

    def test_entity_notion_id_is_mapped(self) -> None:
        service = _make_service(
            {"feedback-db-id": [_raw_feedback(notion_id="feedback-xyz", week="2024-W20")]}
        )
        result = service.sync_weekly_feedback()

        entity = result.entities[0]
        assert isinstance(entity, Feedback)
        assert entity.notion_page_id == "feedback-xyz"
        assert entity.week == "2024-W20"

    def test_malformed_page_increments_failed(self) -> None:
        bad_page: dict[str, Any] = {"id": "bad-feedback", "properties": {}}
        service = _make_service({"feedback-db-id": [bad_page]})
        result = service.sync_weekly_feedback()

        assert result.failed == 1
        assert result.success == 0


# ===========================================================================
# sync_all
# ===========================================================================


class TestSyncAll:
    def _full_service(self) -> NotionSyncService:
        return _make_service(
            {
                "phase-db-id": [_raw_phase("p1")],
                "workout-db-id": [_raw_workout("w1")],
                "session-db-id": [_raw_session("s1")],
                "feedback-db-id": [_raw_feedback("f1")],
            }
        )

    def test_returns_four_results(self) -> None:
        results = self._full_service().sync_all()

        assert len(results) == 4

    def test_result_entities_in_dependency_order(self) -> None:
        results = self._full_service().sync_all()

        assert results[0].entity == "Phase"
        assert results[1].entity == "Workout"
        assert results[2].entity == "TrackedSession"
        assert results[3].entity == "Feedback"

    def test_all_results_are_sync_result_instances(self) -> None:
        results = self._full_service().sync_all()

        assert all(isinstance(r, SyncResult) for r in results)

    def test_all_entities_mapped_successfully(self) -> None:
        results = self._full_service().sync_all()

        assert all(r.success == 1 for r in results)
        assert all(r.failed == 0 for r in results)

    def test_empty_databases_return_zero_counts(self) -> None:
        service = _make_service({})
        results = service.sync_all()

        assert all(r.fetched == 0 for r in results)
        assert all(r.success == 0 for r in results)

    def test_partial_failure_does_not_abort_remaining_syncs(self) -> None:
        bad_page: dict[str, Any] = {"id": "bad", "properties": {}}
        service = _make_service(
            {
                "phase-db-id": [bad_page],  # will fail
                "workout-db-id": [_raw_workout("w1")],
                "session-db-id": [_raw_session("s1")],
                "feedback-db-id": [_raw_feedback("f1")],
            }
        )
        results = service.sync_all()

        assert results[0].failed == 1  # Phase failed
        assert results[1].success == 1  # Workout still ran
        assert results[2].success == 1  # Session still ran
        assert results[3].success == 1  # Feedback still ran

    def test_sync_all_logs_start_and_completion(self, caplog: pytest.LogCaptureFixture) -> None:
        import logging

        with caplog.at_level(logging.INFO, logger="ldk_athlete_ai_coach"):
            self._full_service().sync_all()

        messages = caplog.text
        assert "Starting full Notion sync" in messages
        assert "Full Notion sync completed" in messages
