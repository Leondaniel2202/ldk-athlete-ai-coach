"""API tests for the Notion sync endpoint."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from ldk_athlete_ai_coach.core.integrations.notion.client import (
    NotionAPIError,
    NotionAuthError,
    NotionDatabaseNotFoundError,
    NotionRateLimitError,
)
from ldk_athlete_ai_coach.core.integrations.notion.sync_service import (
    NotionSyncError,
    SyncResult,
)
from ldk_athlete_ai_coach.main import app

client = TestClient(app)


def _result(
    entity: str,
    *,
    fetched: int,
    success: int,
    failed: int,
) -> SyncResult:
    """Build a sync result for route tests."""

    return SyncResult(
        entity=entity,
        fetched=fetched,
        success=success,
        failed=failed,
    )


def test_notion_sync_endpoint_returns_summary_on_success() -> None:
    """Endpoint returns 200 with aggregate and per-entity sync counts."""

    with (
        patch("ldk_athlete_ai_coach.api.v1.notion.NotionClient") as mock_client_cls,
        patch("ldk_athlete_ai_coach.api.v1.notion.NotionSyncService") as mock_service_cls,
    ):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_service = MagicMock()
        mock_service.sync_all.return_value = [
            _result("Phase", fetched=2, success=2, failed=0),
            _result("Workout", fetched=3, success=3, failed=0),
            _result("TrackedSession", fetched=1, success=1, failed=0),
            _result("Feedback", fetched=2, success=2, failed=0),
        ]
        mock_service_cls.return_value = mock_service

        response = client.post("/api/v1/notion/sync")

    assert response.status_code == 200
    assert response.json() == {
        "total_fetched": 8,
        "total_success": 8,
        "total_failed": 0,
        "results": [
            {"entity": "Phase", "fetched": 2, "success": 2, "failed": 0},
            {"entity": "Workout", "fetched": 3, "success": 3, "failed": 0},
            {"entity": "TrackedSession", "fetched": 1, "success": 1, "failed": 0},
            {"entity": "Feedback", "fetched": 2, "success": 2, "failed": 0},
        ],
    }
    mock_client_cls.assert_called_once()
    mock_service_cls.assert_called_once()


def test_notion_sync_endpoint_defaults_hard_fail_to_false() -> None:
    """Endpoint constructs the sync service with hard_fail=False by default."""

    with (
        patch("ldk_athlete_ai_coach.api.v1.notion.NotionClient") as mock_client_cls,
        patch("ldk_athlete_ai_coach.api.v1.notion.NotionSyncService") as mock_service_cls,
    ):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_service = MagicMock()
        mock_service.sync_all.return_value = []
        mock_service_cls.return_value = mock_service

        response = client.post("/api/v1/notion/sync")

    assert response.status_code == 200
    mock_service_cls.assert_called_once()
    assert mock_service_cls.call_args.args[0] is mock_client
    assert mock_service_cls.call_args.kwargs["hard_fail"] is False


def test_notion_sync_endpoint_accepts_hard_fail_query_param() -> None:
    """Endpoint forwards hard_fail=true to the sync service constructor."""

    with (
        patch("ldk_athlete_ai_coach.api.v1.notion.NotionClient") as mock_client_cls,
        patch("ldk_athlete_ai_coach.api.v1.notion.NotionSyncService") as mock_service_cls,
    ):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_service = MagicMock()
        mock_service.sync_all.return_value = []
        mock_service_cls.return_value = mock_service

        response = client.post("/api/v1/notion/sync?hard_fail=true")

    assert response.status_code == 200
    mock_service_cls.assert_called_once()
    assert mock_service_cls.call_args.args[0] is mock_client
    assert mock_service_cls.call_args.kwargs["hard_fail"] is True


def test_notion_sync_endpoint_returns_500_summary_on_partial_failure() -> None:
    """Endpoint returns the sync summary with 500 when any entity fails."""

    with patch("ldk_athlete_ai_coach.api.v1.notion.NotionSyncService") as mock_service_cls:
        mock_service = MagicMock()
        mock_service.sync_all.return_value = [
            _result("Phase", fetched=2, success=2, failed=0),
            _result("Workout", fetched=3, success=1, failed=2),
        ]
        mock_service_cls.return_value = mock_service

        response = client.post("/api/v1/notion/sync")

    assert response.status_code == 500
    assert response.json() == {
        "total_fetched": 5,
        "total_success": 3,
        "total_failed": 2,
        "results": [
            {"entity": "Phase", "fetched": 2, "success": 2, "failed": 0},
            {"entity": "Workout", "fetched": 3, "success": 1, "failed": 2},
        ],
    }


def test_notion_sync_endpoint_translates_rate_limit_errors() -> None:
    """Endpoint returns 503 when the Notion client exhausts rate-limit retries."""

    with patch("ldk_athlete_ai_coach.api.v1.notion.NotionSyncService") as mock_service_cls:
        mock_service = MagicMock()
        mock_service.sync_all.side_effect = NotionRateLimitError("rate limited")
        mock_service_cls.return_value = mock_service

        response = client.post("/api/v1/notion/sync")

    assert response.status_code == 503
    assert response.json() == {"detail": "rate limited"}


def test_notion_sync_endpoint_translates_auth_errors() -> None:
    """Endpoint returns 502 for Notion authentication failures."""

    with patch("ldk_athlete_ai_coach.api.v1.notion.NotionSyncService") as mock_service_cls:
        mock_service = MagicMock()
        mock_service.sync_all.side_effect = NotionAuthError("bad credentials")
        mock_service_cls.return_value = mock_service

        response = client.post("/api/v1/notion/sync")

    assert response.status_code == 502
    assert response.json() == {"detail": "bad credentials"}


def test_notion_sync_endpoint_translates_database_not_found_errors() -> None:
    """Endpoint returns 502 for inaccessible Notion databases."""

    with patch("ldk_athlete_ai_coach.api.v1.notion.NotionSyncService") as mock_service_cls:
        mock_service = MagicMock()
        mock_service.sync_all.side_effect = NotionDatabaseNotFoundError("missing database")
        mock_service_cls.return_value = mock_service

        response = client.post("/api/v1/notion/sync")

    assert response.status_code == 502
    assert response.json() == {"detail": "missing database"}


def test_notion_sync_endpoint_translates_generic_notion_api_errors() -> None:
    """Endpoint returns 502 for other Notion API failures."""

    with patch("ldk_athlete_ai_coach.api.v1.notion.NotionSyncService") as mock_service_cls:
        mock_service = MagicMock()
        mock_service.sync_all.side_effect = NotionAPIError("unexpected notion error")
        mock_service_cls.return_value = mock_service

        response = client.post("/api/v1/notion/sync")

    assert response.status_code == 502
    assert response.json() == {"detail": "unexpected notion error"}


def test_notion_sync_endpoint_translates_unexpected_errors() -> None:
    """Endpoint returns 500 for unexpected sync failures."""

    with patch("ldk_athlete_ai_coach.api.v1.notion.NotionSyncService") as mock_service_cls:
        mock_service = MagicMock()
        mock_service.sync_all.side_effect = RuntimeError("boom")
        mock_service_cls.return_value = mock_service

        response = client.post("/api/v1/notion/sync")

    assert response.status_code == 500
    assert response.json() == {"detail": "Unexpected error during full Notion sync"}


def test_notion_sync_endpoint_translates_hard_fail_sync_error() -> None:
    """Endpoint returns structured details when hard-fail sync raises NotionSyncError."""

    with patch("ldk_athlete_ai_coach.api.v1.notion.NotionSyncService") as mock_service_cls:
        mock_service = MagicMock()
        mock_service.sync_all.side_effect = NotionSyncError(
            entity="Phase",
            stage="extract",
            message="missing required Name",
            notion_id="page-123",
            data_source_id="phase-data-source-id",
        )
        mock_service_cls.return_value = mock_service

        response = client.post("/api/v1/notion/sync?hard_fail=true")

    assert response.status_code == 500
    assert response.json() == {
        "detail": {
            "type": "notion_sync_error",
            "entity": "Phase",
            "stage": "extract",
            "message": "missing required Name",
            "notion_id": "page-123",
            "data_source_id": "phase-data-source-id",
        }
    }
