"""Tests for the Notion API client foundation."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import httpx
import pytest
from notion_client.errors import APIResponseError, HTTPResponseError

from ldk_athlete_ai_coach.core.config import Settings
from ldk_athlete_ai_coach.core.integrations.notion.client import (
    NotionAPIError,
    NotionAuthError,
    NotionClient,
    NotionDatabaseNotFoundError,
    NotionRateLimitError,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_http_response(status: int, body: str = "error") -> httpx.Response:
    """Build a minimal :class:`httpx.Response`.

    Args:
        status: HTTP status code for the synthetic response.
        body: Response text body.

    Returns:
        Response object suitable for constructing Notion SDK errors in tests.
    """
    return httpx.Response(status_code=status, text=body)


def _make_http_error(status: int, message: str = "error") -> HTTPResponseError:
    """Build a :class:`HTTPResponseError`.

    Args:
        status: HTTP status code exposed by the exception response.
        message: Error message attached to the exception.

    Returns:
        HTTPResponseError carrying a synthetic response.
    """
    return HTTPResponseError(response=_make_http_response(status), message=message)


def _make_api_error(
    status: int,
    code: str = "unknown",
    message: str = "error",
) -> APIResponseError:
    """Build an :class:`APIResponseError`.

    Args:
        status: HTTP status code exposed by the exception response.
        code: Notion API error code string.
        message: Error message attached to the exception.

    Returns:
        APIResponseError carrying a synthetic response and code.
    """
    from notion_client.errors import APIErrorCode

    # APIErrorCode is a string enum; cast the raw value so mypy is satisfied.
    try:
        api_code: APIErrorCode = APIErrorCode(code)
    except ValueError:
        api_code = code  # type: ignore[assignment]  # intentional test helper

    return APIResponseError(
        response=_make_http_response(status),
        message=message,
        code=api_code,
    )


def _settings(**overrides: Any) -> Settings:
    """Build a minimal :class:`Settings` object for Notion tests.

    Args:
        **overrides: Setting overrides applied on top of test defaults.

    Returns:
        Settings instance with required database and Notion fields populated.
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


def _make_client(**setting_overrides: Any) -> tuple[NotionClient, MagicMock]:
    """Create a NotionClient with a mocked SDK backend.

    Args:
        **setting_overrides: Optional settings values passed to the test settings factory.

    Returns:
        Tuple containing the constructed client and mocked SDK client.
    """
    settings = _settings(**setting_overrides)
    with patch("ldk_athlete_ai_coach.core.integrations.notion.client.Client") as mock_sdk_cls:
        mock_sdk = MagicMock()
        mock_sdk_cls.return_value = mock_sdk
        client = NotionClient(settings)
    client._client = mock_sdk  # expose for assertions
    return client, mock_sdk


# ---------------------------------------------------------------------------
# get_database
# ---------------------------------------------------------------------------


class TestGetDatabase:
    def test_returns_raw_response(self) -> None:
        """get_database returns the raw API response dict."""
        client, sdk = _make_client()
        expected: dict[str, Any] = {"id": "db-123", "title": []}
        sdk.databases.retrieve.return_value = expected

        result = client.get_database("db-123")

        sdk.databases.retrieve.assert_called_once_with(database_id="db-123")
        assert result is expected

    def test_raises_auth_error_on_401(self) -> None:
        """get_database raises NotionAuthError on HTTP 401."""
        client, sdk = _make_client()
        sdk.databases.retrieve.side_effect = _make_api_error(401, "unauthorized")

        with pytest.raises(NotionAuthError):
            client.get_database("db-123")

    def test_raises_not_found_on_404(self) -> None:
        """get_database raises NotionDatabaseNotFoundError on HTTP 404."""
        client, sdk = _make_client()
        sdk.databases.retrieve.side_effect = _make_api_error(404, "object_not_found")

        with pytest.raises(NotionDatabaseNotFoundError):
            client.get_database("db-123")

    def test_raises_not_found_on_403(self) -> None:
        """get_database raises NotionDatabaseNotFoundError on HTTP 403."""
        client, sdk = _make_client()
        sdk.databases.retrieve.side_effect = _make_api_error(403, "restricted_resource")

        with pytest.raises(NotionDatabaseNotFoundError):
            client.get_database("db-123")

    def test_http_error_401_raises_auth_error(self) -> None:
        """get_database raises NotionAuthError on HTTPResponseError with status 401."""
        client, sdk = _make_client()
        sdk.databases.retrieve.side_effect = _make_http_error(401)

        with pytest.raises(NotionAuthError):
            client.get_database("db-123")

    def test_http_error_403_raises_not_found(self) -> None:
        """get_database raises NotionDatabaseNotFoundError on HTTPResponseError with status 403."""
        client, sdk = _make_client()
        sdk.databases.retrieve.side_effect = _make_http_error(403)

        with pytest.raises(NotionDatabaseNotFoundError):
            client.get_database("db-123")

    def test_http_error_404_raises_not_found(self) -> None:
        """get_database raises NotionDatabaseNotFoundError on HTTPResponseError with status 404."""
        client, sdk = _make_client()
        sdk.databases.retrieve.side_effect = _make_http_error(404)

        with pytest.raises(NotionDatabaseNotFoundError):
            client.get_database("db-123")


# ---------------------------------------------------------------------------
# query_database
# ---------------------------------------------------------------------------


class TestQueryDatabase:
    def test_single_page_result(self) -> None:
        """query_database returns a single page response without a cursor."""
        client, sdk = _make_client()
        payload: dict[str, Any] = {
            "results": [{"id": "page-1"}, {"id": "page-2"}],
            "has_more": False,
            "next_cursor": None,
        }
        sdk.databases.query.return_value = payload

        result = client.query_database("db-123")

        sdk.databases.query.assert_called_once_with(database_id="db-123", page_size=100)
        assert result is payload

    def test_passes_start_cursor(self) -> None:
        """query_database forwards start_cursor to the SDK."""
        client, sdk = _make_client()
        sdk.databases.query.return_value = {"results": [], "has_more": False, "next_cursor": None}

        client.query_database("db-123", start_cursor="cursor-abc")

        sdk.databases.query.assert_called_once_with(
            database_id="db-123",
            page_size=100,
            start_cursor="cursor-abc",
        )

    def test_empty_results(self) -> None:
        """query_database handles an empty result set."""
        client, sdk = _make_client()
        payload: dict[str, Any] = {"results": [], "has_more": False, "next_cursor": None}
        sdk.databases.query.return_value = payload

        result = client.query_database("db-123")

        assert result["results"] == []

    def test_raises_api_error_on_unexpected_status(self) -> None:
        """query_database raises NotionAPIError on unexpected API status codes."""
        client, sdk = _make_client()
        sdk.databases.query.side_effect = _make_api_error(500, "internal_server_error")

        with pytest.raises(NotionAPIError):
            client.query_database("db-123")


# ---------------------------------------------------------------------------
# iter_database_entries
# ---------------------------------------------------------------------------


class TestIterDatabaseEntries:
    def test_single_page_yields_all_results(self) -> None:
        """iter_database_entries yields all items when there is only one page."""
        client, sdk = _make_client()
        sdk.databases.query.return_value = {
            "results": [{"id": "page-1"}, {"id": "page-2"}],
            "has_more": False,
            "next_cursor": None,
        }

        results = list(client.iter_database_entries("db-123"))

        assert len(results) == 2
        assert results[0]["id"] == "page-1"
        assert results[1]["id"] == "page-2"

    def test_multi_page_yields_all_results(self) -> None:
        """iter_database_entries follows pagination cursors until has_more is False."""
        client, sdk = _make_client()
        sdk.databases.query.side_effect = [
            {"results": [{"id": "p1"}, {"id": "p2"}], "has_more": True, "next_cursor": "cur-1"},
            {"results": [{"id": "p3"}, {"id": "p4"}], "has_more": True, "next_cursor": "cur-2"},
            {"results": [{"id": "p5"}], "has_more": False, "next_cursor": None},
        ]

        results = list(client.iter_database_entries("db-123"))

        assert [r["id"] for r in results] == ["p1", "p2", "p3", "p4", "p5"]
        assert sdk.databases.query.call_count == 3
        # First call: no cursor; second: cursor from page 1; third: cursor from page 2.
        assert sdk.databases.query.call_args_list[0][1].get("start_cursor") is None
        assert sdk.databases.query.call_args_list[1][1]["start_cursor"] == "cur-1"
        assert sdk.databases.query.call_args_list[2][1]["start_cursor"] == "cur-2"

    def test_multi_page_passes_cursor(self) -> None:
        """iter_database_entries sends the cursor from one page to the next request."""
        client, sdk = _make_client()
        sdk.databases.query.side_effect = [
            {"results": [{"id": "p1"}], "has_more": True, "next_cursor": "cursor-x"},
            {"results": [{"id": "p2"}], "has_more": False, "next_cursor": None},
        ]

        list(client.iter_database_entries("db-123"))

        second_call_kwargs = sdk.databases.query.call_args_list[1][1]
        assert second_call_kwargs["start_cursor"] == "cursor-x"

    def test_empty_database_yields_nothing(self) -> None:
        """iter_database_entries yields no items for an empty database."""
        client, sdk = _make_client()
        sdk.databases.query.return_value = {"results": [], "has_more": False, "next_cursor": None}

        results = list(client.iter_database_entries("db-123"))

        assert results == []


# ---------------------------------------------------------------------------
# Rate-limit handling
# ---------------------------------------------------------------------------


class TestRateLimitHandling:
    def test_retries_on_http_429_and_succeeds(self) -> None:
        """Client retries on HTTP 429 and returns result when retry succeeds."""
        client, sdk = _make_client(notion_max_retries=3)
        rate_limit_error = _make_http_error(429)
        success_payload: dict[str, Any] = {
            "results": [{"id": "p1"}],
            "has_more": False,
            "next_cursor": None,
        }
        sdk.databases.query.side_effect = [rate_limit_error, success_payload]

        with patch("ldk_athlete_ai_coach.core.integrations.notion.client.time.sleep") as mock_sleep:
            result = client.query_database("db-123")

        mock_sleep.assert_called_once()
        assert result is success_payload

    def test_raises_rate_limit_error_after_retries_exhausted(self) -> None:
        """Client raises NotionRateLimitError after max retries are exhausted."""
        client, sdk = _make_client(notion_max_retries=2)
        sdk.databases.query.side_effect = _make_http_error(429)

        with patch("ldk_athlete_ai_coach.core.integrations.notion.client.time.sleep"):
            with pytest.raises(NotionRateLimitError):
                client.query_database("db-123")

    def test_retries_on_api_response_error_429_and_succeeds(self) -> None:
        """Client retries on APIResponseError 429 and returns result when retry succeeds."""
        client, sdk = _make_client(notion_max_retries=3)
        rate_limit_error = _make_api_error(429, "rate_limited")
        success_payload: dict[str, Any] = {
            "results": [{"id": "p1"}],
            "has_more": False,
            "next_cursor": None,
        }
        sdk.databases.query.side_effect = [rate_limit_error, success_payload]

        with patch("ldk_athlete_ai_coach.core.integrations.notion.client.time.sleep") as mock_sleep:
            result = client.query_database("db-123")

        mock_sleep.assert_called_once()
        assert result is success_payload

    def test_raises_rate_limit_error_when_api_error_retries_exhausted(self) -> None:
        """Client raises NotionRateLimitError on APIResponseError 429 when retries exhausted."""
        client, sdk = _make_client(notion_max_retries=1)
        sdk.databases.query.side_effect = _make_api_error(429, "rate_limited")

        with patch("ldk_athlete_ai_coach.core.integrations.notion.client.time.sleep"):
            with pytest.raises(NotionRateLimitError):
                client.query_database("db-123")


# ---------------------------------------------------------------------------
# Settings validation
# ---------------------------------------------------------------------------


class TestNotionSettings:
    def test_settings_fail_when_notion_api_key_missing(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Any,
    ) -> None:
        """Settings raise ValidationError when NOTION_API_KEY is absent."""
        from pydantic import ValidationError

        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("NOTION_API_KEY", raising=False)
        monkeypatch.delenv("NOTION_PHASE_DB_ID", raising=False)
        monkeypatch.delenv("NOTION_WORKOUT_DB_ID", raising=False)
        monkeypatch.delenv("NOTION_SESSION_DB_ID", raising=False)
        monkeypatch.delenv("NOTION_FEEDBACK_DB_ID", raising=False)
        with pytest.raises(ValidationError):
            Settings(  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]
                postgres_db="db",
                postgres_user="u",
                postgres_password="p",
                postgres_host="h",
                # no notion fields
            )

    def test_settings_accept_all_notion_fields(self) -> None:
        """Settings parse correctly when all required Notion fields are supplied."""
        s = _settings()
        assert s.notion_api_key == "secret_test_key"
        assert s.notion_phase_db_id == "phase-db-id"
        assert s.notion_page_size == 100
        assert s.notion_max_retries == 3
