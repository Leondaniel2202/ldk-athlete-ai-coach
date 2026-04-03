"""Unit tests for the Notion sync service."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from ldk_athlete_ai_coach.core.config import Settings
from ldk_athlete_ai_coach.core.integrations.notion.client import NotionClient
from ldk_athlete_ai_coach.core.integrations.notion.sync_service import (
    NotionSyncService,
    SyncResult,
)
from ldk_athlete_ai_coach.db.models.sport_manager import (
    Feedback,
    NotionSyncMixin,
    Phase,
    TrackedSession,
    Workout,
)


def _settings(**overrides: Any) -> Settings:
    """Build a minimal Settings instance with required fields populated.

    Args:
        **overrides: Setting overrides applied to the default test values.

    Returns:
        Settings instance suitable for Notion sync tests.
    """
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


def _make_service(
    raw_pages_by_db: dict[str, list[dict[str, Any]]],
    *,
    session_factory: MagicMock | None = None,
) -> NotionSyncService:
    """Create a NotionSyncService with controlled raw-page inputs.

    Args:
        raw_pages_by_db: Mapping of database IDs to raw pages yielded by the mock client.
        session_factory: Optional mock session factory.

    Returns:
        Sync service configured with mocked client and session factory.
    """
    settings = _settings()
    client = MagicMock(spec=NotionClient)

    def _iter(database_id: str):
        return iter(raw_pages_by_db.get(database_id, []))

    client.iter_database_entries.side_effect = _iter
    return NotionSyncService(client, settings, session_factory=session_factory or MagicMock())


def _title_prop(text: str) -> dict[str, Any]:
    return {"type": "title", "title": [{"plain_text": text}]}


def _raw_phase(notion_id: str = "phase-1", name: str = "Base Phase") -> dict[str, Any]:
    return {
        "id": notion_id,
        "url": f"https://notion.so/{notion_id}",
        "archived": False,
        "created_time": "2024-03-01T08:00:00.000Z",
        "last_edited_time": "2024-03-01T08:00:00.000Z",
        "properties": {
            "Name": _title_prop(name),
        },
    }


def _raw_workout(notion_id: str = "workout-1", name: str = "Long Run") -> dict[str, Any]:
    return {
        "id": notion_id,
        "url": f"https://notion.so/{notion_id}",
        "archived": False,
        "created_time": "2024-03-01T08:00:00.000Z",
        "last_edited_time": "2024-03-01T08:00:00.000Z",
        "properties": {
            "Name": _title_prop(name),
        },
    }


def _raw_session(notion_id: str = "session-1", name: str = "Morning Run") -> dict[str, Any]:
    return {
        "id": notion_id,
        "url": f"https://notion.so/{notion_id}",
        "archived": False,
        "created_time": "2024-03-01T08:00:00.000Z",
        "last_edited_time": "2024-03-01T08:00:00.000Z",
        "properties": {
            "Name": _title_prop(name),
        },
    }


def _raw_feedback(notion_id: str = "feedback-1", week: str = "2024-W10") -> dict[str, Any]:
    return {
        "id": notion_id,
        "url": f"https://notion.so/{notion_id}",
        "archived": False,
        "created_time": "2024-03-01T08:00:00.000Z",
        "last_edited_time": "2024-03-01T08:00:00.000Z",
        "properties": {
            "Week": _title_prop(week),
        },
    }


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
        r1.entities.append(cast(NotionSyncMixin, object()))

        assert r2.entities == []


class TestSyncPhases:
    def test_persists_all_valid_pages_in_one_batch_and_commits_once(self) -> None:
        session = MagicMock()
        session_factory = MagicMock(return_value=session)
        service = _make_service(
            {"phase-db-id": [_raw_phase("p1"), _raw_phase("p2")]},
            session_factory=session_factory,
        )
        persisted = [Phase(), Phase()]
        persisted[0].notion_page_id = "p1"
        persisted[1].notion_page_id = "p2"

        with patch(
            "ldk_athlete_ai_coach.core.integrations.notion.sync_service.NotionPersistenceService"
        ) as persistence_cls:
            persistence = persistence_cls.return_value
            persistence.persist_phases.return_value = persisted

            result = service.sync_phases()

        assert result.fetched == 2
        assert result.success == 2
        assert result.failed == 0
        assert result.entities == persisted
        persistence.persist_phases.assert_called_once()
        [schemas] = persistence.persist_phases.call_args.args
        assert [schema.notion_id for schema in schemas] == ["p1", "p2"]
        session.commit.assert_called_once_with()
        session.rollback.assert_not_called()
        session.close.assert_called_once_with()

    def test_extraction_failures_do_not_abort_valid_batch(self) -> None:
        session = MagicMock()
        session_factory = MagicMock(return_value=session)
        bad_page: dict[str, Any] = {"id": "bad-phase", "properties": {}}
        service = _make_service(
            {"phase-db-id": [_raw_phase("p1"), bad_page, _raw_phase("p2")]},
            session_factory=session_factory,
        )

        with patch(
            "ldk_athlete_ai_coach.core.integrations.notion.sync_service.NotionPersistenceService"
        ) as persistence_cls:
            persistence = persistence_cls.return_value
            persistence.persist_phases.return_value = [Phase(), Phase()]

            result = service.sync_phases()

        assert result.fetched == 3
        assert result.success == 2
        assert result.failed == 1
        persistence.persist_phases.assert_called_once()
        [schemas] = persistence.persist_phases.call_args.args
        assert [schema.notion_id for schema in schemas] == ["p1", "p2"]
        session.commit.assert_called_once_with()

    def test_persistence_failure_rolls_back_the_batch(self) -> None:
        session = MagicMock()
        session_factory = MagicMock(return_value=session)
        service = _make_service(
            {"phase-db-id": [_raw_phase("p1"), _raw_phase("p2")]},
            session_factory=session_factory,
        )

        with patch(
            "ldk_athlete_ai_coach.core.integrations.notion.sync_service.NotionPersistenceService"
        ) as persistence_cls:
            persistence = persistence_cls.return_value
            persistence.persist_phases.side_effect = RuntimeError("db error")

            result = service.sync_phases()

        assert result.fetched == 2
        assert result.success == 0
        assert result.failed == 2
        assert result.entities == []
        session.commit.assert_not_called()
        session.rollback.assert_called_once_with()
        session.close.assert_called_once_with()


class TestOtherEntitySyncs:
    def test_sync_workouts_returns_persisted_workouts(self) -> None:
        session = MagicMock()
        service = _make_service(
            {"workout-db-id": [_raw_workout("w1"), _raw_workout("w2")]},
            session_factory=MagicMock(return_value=session),
        )
        persisted = [Workout(), Workout()]

        with patch(
            "ldk_athlete_ai_coach.core.integrations.notion.sync_service.NotionPersistenceService"
        ) as persistence_cls:
            persistence = persistence_cls.return_value
            persistence.persist_workouts.return_value = persisted

            result = service.sync_workouts()

        assert result.entity == "Workout"
        assert result.success == 2
        assert result.entities == persisted
        persistence.persist_workouts.assert_called_once()

    def test_sync_sessions_returns_persisted_tracked_sessions(self) -> None:
        session = MagicMock()
        service = _make_service(
            {"session-db-id": [_raw_session("s1")]},
            session_factory=MagicMock(return_value=session),
        )
        persisted = [TrackedSession()]

        with patch(
            "ldk_athlete_ai_coach.core.integrations.notion.sync_service.NotionPersistenceService"
        ) as persistence_cls:
            persistence = persistence_cls.return_value
            persistence.persist_sessions.return_value = persisted

            result = service.sync_sessions()

        assert result.entity == "TrackedSession"
        assert result.success == 1
        assert result.entities == persisted
        persistence.persist_sessions.assert_called_once()

    def test_sync_weekly_feedback_returns_persisted_feedback(self) -> None:
        session = MagicMock()
        service = _make_service(
            {"feedback-db-id": [_raw_feedback("f1")]},
            session_factory=MagicMock(return_value=session),
        )
        persisted = [Feedback()]

        with patch(
            "ldk_athlete_ai_coach.core.integrations.notion.sync_service.NotionPersistenceService"
        ) as persistence_cls:
            persistence = persistence_cls.return_value
            persistence.persist_feedback.return_value = persisted

            result = service.sync_weekly_feedback()

        assert result.entity == "Feedback"
        assert result.success == 1
        assert result.entities == persisted
        persistence.persist_feedback.assert_called_once()


class TestSyncAll:
    def test_sync_all_continues_after_one_entity_persistence_failure(self) -> None:
        sessions = [MagicMock(name="phase_session"), MagicMock(name="workout_session")]
        sessions.extend([MagicMock(name="tracked_session"), MagicMock(name="feedback_session")])
        service = _make_service(
            {
                "phase-db-id": [_raw_phase("p1")],
                "workout-db-id": [_raw_workout("w1")],
                "session-db-id": [_raw_session("s1")],
                "feedback-db-id": [_raw_feedback("f1")],
            },
            session_factory=MagicMock(side_effect=sessions),
        )

        with patch(
            "ldk_athlete_ai_coach.core.integrations.notion.sync_service.NotionPersistenceService"
        ) as persistence_cls:
            persistence = persistence_cls.return_value
            persistence.persist_phases.side_effect = RuntimeError("phase db error")
            persistence.persist_workouts.return_value = [Workout()]
            persistence.persist_sessions.return_value = [TrackedSession()]
            persistence.persist_feedback.return_value = [Feedback()]

            results = service.sync_all()

        assert [result.entity for result in results] == [
            "Phase",
            "Workout",
            "TrackedSession",
            "Feedback",
        ]
        assert results[0].success == 0
        assert results[0].failed == 1
        assert results[1].success == 1
        assert results[2].success == 1
        assert results[3].success == 1
        sessions[0].rollback.assert_called_once_with()
        sessions[1].commit.assert_called_once_with()
        sessions[2].commit.assert_called_once_with()
        sessions[3].commit.assert_called_once_with()

    def test_sync_all_logs_start_and_completion(self, caplog: pytest.LogCaptureFixture) -> None:
        service = _make_service({})

        with caplog.at_level("INFO", logger="ldk_athlete_ai_coach"):
            results = service.sync_all()

        assert len(results) == 4
        assert "Starting full Notion sync" in caplog.text
        assert "Full Notion sync completed" in caplog.text
