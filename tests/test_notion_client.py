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


def _make_http_response(status: int, body: str = "error") -> httpx.Response:
    """Build a minimal :class:`httpx.Response`."""
    return httpx.Response(status_code=status, text=body)


def _make_http_error(status: int, message: str = "error") -> HTTPResponseError:
    """Build a :class:`HTTPResponseError`."""
    return HTTPResponseError(response=_make_http_response(status), message=message)


def _make_api_error(
    status: int,
    code: str = "unknown",
    message: str = "error",
) -> APIResponseError:
    """Build an :class:`APIResponseError`."""
    from notion_client.errors import APIErrorCode

    try:
        api_code: APIErrorCode = APIErrorCode(code)
    except ValueError:
        api_code = code  # type: ignore[assignment]

    return APIResponseError(
        response=_make_http_response(status),
        message=message,
        code=api_code,
    )


def _settings(**overrides: Any) -> Settings:
    """Build a minimal :class:`Settings` object for Notion tests."""
    defaults: dict[str, Any] = {
        "postgres_db": "test_db",
        "postgres_user": "postgres",
        "postgres_password": "postgres",
        "postgres_host": "localhost",
        "postgres_port": 5432,
        "notion_api_key": "secret_test_key",
        "notion_plan_data_source_id": "plan-data-source-id",
        "notion_phase_data_source_id": "phase-data-source-id",
        "notion_nutrition_guideline_data_source_id": "nutrition-data-source-id",
        "notion_workout_data_source_id": "workout-data-source-id",
        "notion_event_data_source_id": "event-data-source-id",
        "notion_session_data_source_id": "session-data-source-id",
        "notion_feedback_data_source_id": "feedback-data-source-id",
        "notion_page_size": 100,
        "notion_timeout_seconds": 30,
        "notion_max_retries": 3,
    }
    defaults.update(overrides)
    return Settings(**defaults)  # pyright: ignore[reportCallIssue]


def _make_client(**setting_overrides: Any) -> tuple[NotionClient, MagicMock]:
    """Create a NotionClient with a mocked SDK backend."""
    settings = _settings(**setting_overrides)
    with patch("ldk_athlete_ai_coach.core.integrations.notion.client.Client") as mock_sdk_cls:
        mock_sdk = MagicMock()
        mock_sdk_cls.return_value = mock_sdk
        client = NotionClient(settings)
        mock_sdk_cls.assert_called_once_with(
            auth="secret_test_key",
            timeout_ms=30_000,
            notion_version="2026-03-11",
        )
    client._client = mock_sdk
    return client, mock_sdk


class TestGetDatabase:
    def test_returns_raw_response(self) -> None:
        client, sdk = _make_client()
        expected: dict[str, Any] = {"id": "db-123", "title": []}
        sdk.databases.retrieve.return_value = expected

        result = client.get_database("db-123")

        sdk.databases.retrieve.assert_called_once_with(database_id="db-123")
        assert result is expected

    def test_raises_auth_error_on_401(self) -> None:
        client, sdk = _make_client()
        sdk.databases.retrieve.side_effect = _make_api_error(401, "unauthorized")

        with pytest.raises(NotionAuthError):
            client.get_database("db-123")


class TestGetDataSource:
    def test_returns_raw_response(self) -> None:
        client, sdk = _make_client()
        expected: dict[str, Any] = {"id": "ds-123", "object": "data_source"}
        sdk.request.return_value = expected

        result = client.get_data_source("ds-123")

        sdk.request.assert_called_once_with(path="data_sources/ds-123", method="GET")
        assert result is expected

    def test_raises_not_found_on_404(self) -> None:
        client, sdk = _make_client()
        sdk.request.side_effect = _make_http_error(404)

        with pytest.raises(NotionDatabaseNotFoundError):
            client.get_data_source("ds-123")


class TestQueryDataSource:
    def test_single_page_result(self) -> None:
        client, sdk = _make_client()
        payload: dict[str, Any] = {
            "results": [{"id": "page-1"}, {"id": "page-2"}],
            "has_more": False,
            "next_cursor": None,
        }
        sdk.request.return_value = payload

        result = client.query_data_source("ds-123")

        sdk.request.assert_called_once_with(
            path="data_sources/ds-123/query",
            method="POST",
            body={"page_size": 100},
        )
        assert result is payload

    def test_passes_start_cursor(self) -> None:
        client, sdk = _make_client()
        sdk.request.return_value = {"results": [], "has_more": False, "next_cursor": None}

        client.query_data_source("ds-123", start_cursor="cursor-abc")

        sdk.request.assert_called_once_with(
            path="data_sources/ds-123/query",
            method="POST",
            body={"page_size": 100, "start_cursor": "cursor-abc"},
        )

    def test_raises_api_error_on_unexpected_status(self) -> None:
        client, sdk = _make_client()
        sdk.request.side_effect = _make_api_error(500, "internal_server_error")

        with pytest.raises(NotionAPIError):
            client.query_data_source("ds-123")

    def test_backward_compatible_query_database_alias_uses_data_source_query(self) -> None:
        client, sdk = _make_client()
        sdk.request.return_value = {"results": [], "has_more": False, "next_cursor": None}

        client.query_database("ds-123")

        sdk.request.assert_called_once_with(
            path="data_sources/ds-123/query",
            method="POST",
            body={"page_size": 100},
        )


class TestIterDataSourceEntries:
    def test_single_page_yields_all_results(self) -> None:
        client, sdk = _make_client()
        sdk.request.return_value = {
            "results": [{"id": "page-1"}, {"id": "page-2"}],
            "has_more": False,
            "next_cursor": None,
        }

        results = list(client.iter_data_source_entries("ds-123"))

        assert len(results) == 2
        assert results[0]["id"] == "page-1"
        assert results[1]["id"] == "page-2"

    def test_multi_page_yields_all_results(self) -> None:
        client, sdk = _make_client()
        sdk.request.side_effect = [
            {"results": [{"id": "p1"}, {"id": "p2"}], "has_more": True, "next_cursor": "cur-1"},
            {"results": [{"id": "p3"}, {"id": "p4"}], "has_more": True, "next_cursor": "cur-2"},
            {"results": [{"id": "p5"}], "has_more": False, "next_cursor": None},
        ]

        results = list(client.iter_data_source_entries("ds-123"))

        assert [r["id"] for r in results] == ["p1", "p2", "p3", "p4", "p5"]
        assert sdk.request.call_count == 3
        assert sdk.request.call_args_list[0][1]["body"] == {"page_size": 100}
        assert sdk.request.call_args_list[1][1]["body"] == {
            "page_size": 100,
            "start_cursor": "cur-1",
        }
        assert sdk.request.call_args_list[2][1]["body"] == {
            "page_size": 100,
            "start_cursor": "cur-2",
        }

    def test_backward_compatible_iter_database_entries_alias(self) -> None:
        client, sdk = _make_client()
        sdk.request.return_value = {"results": [], "has_more": False, "next_cursor": None}

        results = list(client.iter_database_entries("ds-123"))

        assert results == []


class TestBlockChildren:
    def test_get_block_children_returns_raw_response(self) -> None:
        client, sdk = _make_client()
        expected: dict[str, Any] = {
            "results": [{"id": "block-1"}],
            "has_more": False,
            "next_cursor": None,
        }
        sdk.blocks.children.list.return_value = expected

        result = client.get_block_children("page-123")

        sdk.blocks.children.list.assert_called_once_with(block_id="page-123", page_size=100)
        assert result is expected

    def test_iter_block_children_paginates(self) -> None:
        client, sdk = _make_client()
        sdk.blocks.children.list.side_effect = [
            {
                "results": [{"id": "block-1"}],
                "has_more": True,
                "next_cursor": "cursor-1",
            },
            {
                "results": [{"id": "block-2"}],
                "has_more": False,
                "next_cursor": None,
            },
        ]

        results = list(client.iter_block_children("page-123"))

        assert [block["id"] for block in results] == ["block-1", "block-2"]
        assert sdk.blocks.children.list.call_args_list[0][1] == {
            "block_id": "page-123",
            "page_size": 100,
        }
        assert sdk.blocks.children.list.call_args_list[1][1] == {
            "block_id": "page-123",
            "page_size": 100,
            "start_cursor": "cursor-1",
        }

    def test_get_page_plain_text_flattens_nested_blocks(self) -> None:
        client, sdk = _make_client()
        sdk.blocks.children.list.side_effect = [
            {
                "results": [
                    {
                        "id": "block-1",
                        "type": "heading_2",
                        "heading_2": {"rich_text": [{"plain_text": "Warm-up"}]},
                        "has_children": False,
                    },
                    {
                        "id": "block-2",
                        "type": "toggle",
                        "toggle": {"rich_text": [{"plain_text": "Main Set"}]},
                        "has_children": True,
                    },
                    {
                        "id": "block-3",
                        "type": "table_row",
                        "table_row": {
                            "cells": [
                                [{"plain_text": "Pace"}],
                                [{"plain_text": "4:20/km"}],
                            ]
                        },
                        "has_children": False,
                    },
                ],
                "has_more": False,
                "next_cursor": None,
            },
            {
                "results": [
                    {
                        "id": "block-2-1",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {"rich_text": [{"plain_text": "6 x 800m"}]},
                        "has_children": False,
                    }
                ],
                "has_more": False,
                "next_cursor": None,
            },
        ]

        result = client.get_page_plain_text("page-123")

        assert result == "Warm-up\nMain Set\n6 x 800m\nPace | 4:20/km"

    def test_get_page_plain_text_returns_none_for_empty_pages(self) -> None:
        client, sdk = _make_client()
        sdk.blocks.children.list.return_value = {
            "results": [
                {
                    "id": "block-1",
                    "type": "divider",
                    "divider": {},
                    "has_children": False,
                }
            ],
            "has_more": False,
            "next_cursor": None,
        }

        assert client.get_page_plain_text("page-123") is None


class TestRateLimitHandling:
    def test_retries_on_http_429_and_succeeds(self) -> None:
        client, sdk = _make_client(notion_max_retries=3)
        rate_limit_error = _make_http_error(429)
        success_payload: dict[str, Any] = {
            "results": [{"id": "p1"}],
            "has_more": False,
            "next_cursor": None,
        }
        sdk.request.side_effect = [rate_limit_error, success_payload]

        with patch("ldk_athlete_ai_coach.core.integrations.notion.client.time.sleep") as mock_sleep:
            result = client.query_data_source("ds-123")

        mock_sleep.assert_called_once()
        assert result is success_payload

    def test_raises_rate_limit_error_after_retries_exhausted(self) -> None:
        client, sdk = _make_client(notion_max_retries=2)
        sdk.request.side_effect = _make_http_error(429)

        with patch("ldk_athlete_ai_coach.core.integrations.notion.client.time.sleep"):
            with pytest.raises(NotionRateLimitError):
                client.query_data_source("ds-123")

    def test_retries_on_api_response_error_429_and_succeeds(self) -> None:
        client, sdk = _make_client(notion_max_retries=3)
        rate_limit_error = _make_api_error(429, "rate_limited")
        success_payload: dict[str, Any] = {
            "results": [{"id": "p1"}],
            "has_more": False,
            "next_cursor": None,
        }
        sdk.request.side_effect = [rate_limit_error, success_payload]

        with patch("ldk_athlete_ai_coach.core.integrations.notion.client.time.sleep") as mock_sleep:
            result = client.query_data_source("ds-123")

        mock_sleep.assert_called_once()
        assert result is success_payload

    def test_raises_rate_limit_error_when_api_error_retries_exhausted(self) -> None:
        client, sdk = _make_client(notion_max_retries=1)
        sdk.request.side_effect = _make_api_error(429, "rate_limited")

        with patch("ldk_athlete_ai_coach.core.integrations.notion.client.time.sleep"):
            with pytest.raises(NotionRateLimitError):
                client.query_data_source("ds-123")


class TestNotionSettings:
    def test_settings_fail_when_notion_api_key_missing(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Any,
    ) -> None:
        from pydantic import ValidationError

        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("NOTION_API_KEY", raising=False)
        monkeypatch.delenv("NOTION_PLAN_DATA_SOURCE_ID", raising=False)
        monkeypatch.delenv("NOTION_PHASE_DATA_SOURCE_ID", raising=False)
        monkeypatch.delenv("NOTION_NUTRITION_GUIDELINE_DATA_SOURCE_ID", raising=False)
        monkeypatch.delenv("NOTION_WORKOUT_DATA_SOURCE_ID", raising=False)
        monkeypatch.delenv("NOTION_EVENT_DATA_SOURCE_ID", raising=False)
        monkeypatch.delenv("NOTION_SESSION_DATA_SOURCE_ID", raising=False)
        monkeypatch.delenv("NOTION_FEEDBACK_DATA_SOURCE_ID", raising=False)
        monkeypatch.delenv("NOTION_PLAN_DB_ID", raising=False)
        monkeypatch.delenv("NOTION_PHASE_DB_ID", raising=False)
        monkeypatch.delenv("NOTION_NUTRITION_GUIDELINE_DB_ID", raising=False)
        monkeypatch.delenv("NOTION_WORKOUT_DB_ID", raising=False)
        monkeypatch.delenv("NOTION_EVENT_DB_ID", raising=False)
        monkeypatch.delenv("NOTION_SESSION_DB_ID", raising=False)
        monkeypatch.delenv("NOTION_FEEDBACK_DB_ID", raising=False)
        with pytest.raises(ValidationError):
            Settings(  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]
                postgres_db="db",
                postgres_user="u",
                postgres_password="p",
                postgres_host="h",
            )

    def test_settings_accept_all_notion_fields(self) -> None:
        settings = _settings()

        assert settings.notion_api_key == "secret_test_key"
        assert settings.notion_plan_data_source_id == "plan-data-source-id"
        assert settings.notion_phase_data_source_id == "phase-data-source-id"
        assert settings.notion_nutrition_guideline_data_source_id == "nutrition-data-source-id"
        assert settings.notion_event_data_source_id == "event-data-source-id"
        assert settings.notion_page_size == 100
        assert settings.notion_max_retries == 3

    def test_settings_accept_legacy_db_env_names(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any
    ) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("POSTGRES_DB", "db")
        monkeypatch.setenv("POSTGRES_USER", "user")
        monkeypatch.setenv("POSTGRES_PASSWORD", "password")
        monkeypatch.setenv("POSTGRES_HOST", "localhost")
        monkeypatch.setenv("NOTION_API_KEY", "secret")
        monkeypatch.delenv("NOTION_PLAN_DATA_SOURCE_ID", raising=False)
        monkeypatch.delenv("NOTION_PHASE_DATA_SOURCE_ID", raising=False)
        monkeypatch.delenv("NOTION_NUTRITION_GUIDELINE_DATA_SOURCE_ID", raising=False)
        monkeypatch.delenv("NOTION_WORKOUT_DATA_SOURCE_ID", raising=False)
        monkeypatch.delenv("NOTION_EVENT_DATA_SOURCE_ID", raising=False)
        monkeypatch.delenv("NOTION_SESSION_DATA_SOURCE_ID", raising=False)
        monkeypatch.delenv("NOTION_FEEDBACK_DATA_SOURCE_ID", raising=False)
        monkeypatch.setenv("NOTION_PLAN_DB_ID", "legacy-plan")
        monkeypatch.setenv("NOTION_PHASE_DB_ID", "legacy-phase")
        monkeypatch.setenv("NOTION_NUTRITION_GUIDELINE_DB_ID", "legacy-nutrition")
        monkeypatch.setenv("NOTION_WORKOUT_DB_ID", "legacy-workout")
        monkeypatch.setenv("NOTION_EVENT_DB_ID", "legacy-event")
        monkeypatch.setenv("NOTION_SESSION_DB_ID", "legacy-session")
        monkeypatch.setenv("NOTION_FEEDBACK_DB_ID", "legacy-feedback")

        settings = Settings()  # type: ignore[call-arg]  # pyright: ignore[reportCallIssue]

        assert settings.notion_plan_data_source_id == "legacy-plan"
        assert settings.notion_phase_data_source_id == "legacy-phase"
        assert settings.notion_nutrition_guideline_data_source_id == "legacy-nutrition"
        assert settings.notion_workout_data_source_id == "legacy-workout"
        assert settings.notion_event_data_source_id == "legacy-event"
        assert settings.notion_session_data_source_id == "legacy-session"
        assert settings.notion_feedback_data_source_id == "legacy-feedback"
