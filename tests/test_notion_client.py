"""Tests for the Notion API client."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ldk_athlete_ai_coach.core.config import Settings
from ldk_athlete_ai_coach.core.integrations.notion.client import (
    NotionAuthError,
    NotionClient,
    NotionConfigError,
    NotionDatabaseError,
    NotionRateLimitError,
)


@pytest.fixture()
def client() -> NotionClient:
    """Return a NotionClient instance with a dummy API key."""
    return NotionClient(api_key="test-key", max_retries=2)


@pytest.fixture()
def base_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Settings:
    """Return a Settings instance with minimal required fields set."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("POSTGRES_DB", "db")
    monkeypatch.setenv("POSTGRES_USER", "user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.delenv("NOTION_API_KEY", raising=False)
    return Settings()  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]


def _mock_response(status_code: int, body: dict | None = None) -> MagicMock:
    """Build a mock httpx response."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = body or {}
    mock.headers = {}
    return mock


# ---------------------------------------------------------------------------
# query_database
# ---------------------------------------------------------------------------


def test_query_database_returns_raw_response(client: NotionClient) -> None:
    """Single-page query returns the raw Notion response unchanged."""
    body = {"results": [{"id": "page-1"}, {"id": "page-2"}], "has_more": False}
    with patch.object(client._http, "request", return_value=_mock_response(200, body)):
        result = client.query_database("db-123")
    assert result == body


def test_query_database_sends_start_cursor(client: NotionClient) -> None:
    """A start_cursor is forwarded to the Notion API request body."""
    body = {"results": [], "has_more": False}
    with patch.object(client._http, "request", return_value=_mock_response(200, body)) as mock_req:
        client.query_database("db-123", start_cursor="cursor-abc")
    _, kwargs = mock_req.call_args
    assert kwargs["json"]["start_cursor"] == "cursor-abc"


# ---------------------------------------------------------------------------
# query_all_pages — pagination
# ---------------------------------------------------------------------------


def test_query_all_pages_single_page(client: NotionClient) -> None:
    """A single-page database returns all results in one call."""
    body = {"results": [{"id": "p1"}, {"id": "p2"}], "has_more": False}
    with patch.object(client._http, "request", return_value=_mock_response(200, body)):
        results = client.query_all_pages("db-123")
    assert results == [{"id": "p1"}, {"id": "p2"}]


def test_query_all_pages_handles_pagination(client: NotionClient) -> None:
    """Results from multiple pages are merged into a single list."""
    page1 = {"results": [{"id": "p1"}], "has_more": True, "next_cursor": "cur-1"}
    page2 = {"results": [{"id": "p2"}], "has_more": True, "next_cursor": "cur-2"}
    page3 = {"results": [{"id": "p3"}], "has_more": False}

    responses = iter([page1, page2, page3])

    with patch.object(
        client._http,
        "request",
        side_effect=lambda *a, **kw: _mock_response(200, next(responses)),
    ):
        results = client.query_all_pages("db-123")

    assert results == [{"id": "p1"}, {"id": "p2"}, {"id": "p3"}]


def test_query_all_pages_empty_database(client: NotionClient) -> None:
    """An empty database returns an empty list."""
    body = {"results": [], "has_more": False}
    with patch.object(client._http, "request", return_value=_mock_response(200, body)):
        results = client.query_all_pages("db-123")
    assert results == []


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def test_auth_error_raised_on_401(client: NotionClient) -> None:
    """HTTP 401 raises NotionAuthError."""
    with patch.object(client._http, "request", return_value=_mock_response(401)):
        with pytest.raises(NotionAuthError):
            client.query_database("db-123")


def test_database_error_raised_on_404(client: NotionClient) -> None:
    """HTTP 404 raises NotionDatabaseError."""
    with patch.object(client._http, "request", return_value=_mock_response(404)):
        with pytest.raises(NotionDatabaseError):
            client.query_database("db-123")


def test_database_error_raised_on_403(client: NotionClient) -> None:
    """HTTP 403 raises NotionDatabaseError."""
    with patch.object(client._http, "request", return_value=_mock_response(403)):
        with pytest.raises(NotionDatabaseError):
            client.query_database("db-123")


def test_rate_limit_retries_then_raises(client: NotionClient) -> None:
    """HTTP 429 is retried up to max_retries times, then raises NotionRateLimitError."""
    rate_limited = _mock_response(429)
    rate_limited.headers = {"Retry-After": "0"}

    with patch.object(client._http, "request", return_value=rate_limited):
        with patch("ldk_athlete_ai_coach.core.integrations.notion.client.time.sleep"):
            with pytest.raises(NotionRateLimitError):
                client.query_database("db-123")


def test_rate_limit_retries_succeed_on_recovery(client: NotionClient) -> None:
    """After a 429, a subsequent 200 is returned successfully."""
    rate_limited = _mock_response(429)
    rate_limited.headers = {"Retry-After": "0"}
    success_body = {"results": [{"id": "p1"}], "has_more": False}
    success = _mock_response(200, success_body)

    responses = iter([rate_limited, success])

    with patch.object(
        client._http,
        "request",
        side_effect=lambda *a, **kw: next(responses),
    ):
        with patch("ldk_athlete_ai_coach.core.integrations.notion.client.time.sleep"):
            result = client.query_database("db-123")

    assert result == success_body


# ---------------------------------------------------------------------------
# from_settings
# ---------------------------------------------------------------------------


def test_from_settings_raises_config_error_when_api_key_missing(
    base_settings: Settings,
) -> None:
    """from_settings raises NotionConfigError if notion_api_key is not set."""
    with pytest.raises(NotionConfigError):
        NotionClient.from_settings(base_settings)


def test_from_settings_creates_client_when_api_key_is_set(
    base_settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """from_settings returns a NotionClient when notion_api_key is configured."""
    monkeypatch.setattr(base_settings, "notion_api_key", "secret-key")
    notion_client = NotionClient.from_settings(base_settings)
    assert isinstance(notion_client, NotionClient)
