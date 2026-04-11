"""Notion API client foundation.

This module provides a low-level, reusable Notion client built on top of the official
``notion-client`` SDK. It handles authentication, database and data source retrieval,
automatic pagination for data source queries, basic rate-limit handling, and
structured logging.

Higher-level components such as extractors, mappers, and sync services should import and
use :class:`NotionClient` rather than interacting with the SDK directly.

Typical usage::

    from ldk_athlete_ai_coach.core.integrations.notion.client import NotionClient
    from ldk_athlete_ai_coach.core.config import get_settings

    client = NotionClient(get_settings())

    # Retrieve the database container metadata
    database = client.get_database(database_id="<uuid>")

    # Retrieve a data source definition
    data_source = client.get_data_source(data_source_id="<uuid>")

    # Fetch a single page of entries from a data source
    page = client.query_data_source(data_source_id="<uuid>")

    # Iterate over all entries across all query pages
    for entry in client.iter_data_source_entries(data_source_id="<uuid>"):
        ...
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from typing import Any, NoReturn

from notion_client import Client
from notion_client.errors import APIResponseError, HTTPResponseError

from ldk_athlete_ai_coach.core.config import Settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class NotionClientError(Exception):
    """Base exception for all Notion client errors."""


class NotionAuthError(NotionClientError):
    """Raised when authentication with the Notion API fails."""


class NotionDatabaseNotFoundError(NotionClientError):
    """Raised when the requested database or data source cannot be found or accessed."""


class NotionRateLimitError(NotionClientError):
    """Raised when rate-limit retries are exhausted."""


class NotionAPIError(NotionClientError):
    """Raised for unexpected Notion API response errors."""


# ---------------------------------------------------------------------------
# HTTP status codes
# ---------------------------------------------------------------------------

_HTTP_UNAUTHORIZED = 401
_HTTP_FORBIDDEN = 403
_HTTP_NOT_FOUND = 404
_HTTP_TOO_MANY_REQUESTS = 429
_DEFAULT_RETRY_WAIT_SECONDS = 1.0
_NOTION_API_VERSION = "2026-03-11"


# ---------------------------------------------------------------------------
# NotionClient
# ---------------------------------------------------------------------------


class NotionClient:
    """Low-level Notion API client.

    Wraps the official ``notion-client`` SDK to provide:

    * Authenticated access using the configured ``NOTION_API_KEY``.
    * Database container retrieval (:meth:`get_database`).
    * Data source retrieval (:meth:`get_data_source`).
    * Single-page data source queries (:meth:`query_data_source`).
    * Full paginated iteration over data source entries (:meth:`iter_data_source_entries`).
    * Basic 429 rate-limit handling with configurable retries.
    * Structured logging for all major operations.

    All methods return raw Notion API response payloads. No extraction, mapping, or
    persistence is performed here.

    Args:
        settings: Application settings instance providing Notion credentials and options.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = Client(
            auth=settings.notion_api_key,
            timeout_ms=settings.notion_timeout_seconds * 1000,
            notion_version=_NOTION_API_VERSION,
        )
        logger.debug(
            "NotionClient initialised (timeout=%ds notion_version=%s)",
            settings.notion_timeout_seconds,
            _NOTION_API_VERSION,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_database(self, database_id: str) -> dict[str, Any]:
        """Retrieve metadata for a Notion database container.

        Args:
            database_id: The UUID of the target Notion database container.

        Returns:
            Raw Notion database object as returned by the API.
        """
        logger.debug("Fetching database metadata for database_id=%s", database_id)
        return self._call(self._client.databases.retrieve, database_id=database_id)

    def get_data_source(self, data_source_id: str) -> dict[str, Any]:
        """Retrieve metadata for a Notion data source.

        Args:
            data_source_id: The UUID of the target Notion data source.

        Returns:
            Raw Notion data source object as returned by the API.
        """
        logger.debug("Fetching data source metadata for data_source_id=%s", data_source_id)
        return self._call(
            self._client.request,
            path=f"data_sources/{data_source_id}",
            method="GET",
        )

    def query_data_source(
        self,
        data_source_id: str,
        start_cursor: str | None = None,
    ) -> dict[str, Any]:
        """Query a Notion data source and return a single page of results.

        Args:
            data_source_id: The UUID of the target Notion data source.
            start_cursor: Optional pagination cursor returned by a previous query.

        Returns:
            Raw Notion query response (``results``, ``has_more``, ``next_cursor``, ...).
        """
        logger.debug(
            "Querying data_source_id=%s start_cursor=%s page_size=%d",
            data_source_id,
            start_cursor,
            self._settings.notion_page_size,
        )
        body: dict[str, Any] = {
            "page_size": self._settings.notion_page_size,
        }
        if start_cursor is not None:
            body["start_cursor"] = start_cursor

        response: dict[str, Any] = self._call(
            self._client.request,
            path=f"data_sources/{data_source_id}/query",
            method="POST",
            body=body,
        )
        result_count = len(response.get("results", []))
        logger.debug("Fetched %d result(s) from data_source_id=%s", result_count, data_source_id)
        return response

    def iter_data_source_entries(self, data_source_id: str) -> Iterator[dict[str, Any]]:
        """Iterate over every individual entry in a data source, handling pagination.

        Args:
            data_source_id: The UUID of the target Notion data source.

        Yields:
            Individual raw Notion page objects from the data source query results.
        """
        cursor: str | None = None
        total = 0

        while True:
            response = self.query_data_source(data_source_id, start_cursor=cursor)
            results: list[dict[str, Any]] = response.get("results", [])
            total += len(results)
            yield from results

            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

        logger.info(
            "Finished paginated query for data_source_id=%s total_results=%d",
            data_source_id,
            total,
        )

    def query_database(
        self,
        database_id: str,
        start_cursor: str | None = None,
    ) -> dict[str, Any]:
        """Backward-compatible alias for :meth:`query_data_source`.

        The caller must pass a Notion data source ID even though the parameter name
        remains ``database_id`` for compatibility with older code.
        """
        return self.query_data_source(database_id, start_cursor=start_cursor)

    def iter_database_entries(self, database_id: str) -> Iterator[dict[str, Any]]:
        """Backward-compatible alias for :meth:`iter_data_source_entries`."""
        return self.iter_data_source_entries(database_id)

    def get_block_children(
        self,
        block_id: str,
        start_cursor: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve a single page of children for a block or page."""
        kwargs: dict[str, Any] = {
            "block_id": block_id,
            "page_size": self._settings.notion_page_size,
        }
        if start_cursor is not None:
            kwargs["start_cursor"] = start_cursor
        return self._call(self._client.blocks.children.list, **kwargs)

    def iter_block_children(self, block_id: str) -> Iterator[dict[str, Any]]:
        """Iterate over all children for a block or page, handling pagination."""
        cursor: str | None = None

        while True:
            response = self.get_block_children(block_id, start_cursor=cursor)
            results: list[dict[str, Any]] = response.get("results", [])
            yield from results

            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

    def get_page_plain_text(self, page_id: str) -> str | None:
        """Flatten a page body into newline-delimited plain text."""
        lines = self._get_block_plain_text_lines(page_id)
        text = "\n".join(line for line in lines if line).strip()
        return text or None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_block_plain_text_lines(self, block_id: str) -> list[str]:
        """Collect plain-text lines for a block tree."""
        lines: list[str] = []
        for block in self.iter_block_children(block_id):
            text = self._extract_block_plain_text(block)
            if text:
                lines.append(text)
            if block.get("has_children"):
                child_id = block.get("id")
                if isinstance(child_id, str):
                    lines.extend(self._get_block_plain_text_lines(child_id))
        return lines

    @staticmethod
    def _extract_block_plain_text(block: dict[str, Any]) -> str | None:
        """Extract the most useful plain-text representation for a single block."""
        block_type = block.get("type")
        if not isinstance(block_type, str):
            return None

        payload = block.get(block_type)
        if not isinstance(payload, dict):
            return None

        rich_text = payload.get("rich_text")
        if isinstance(rich_text, list):
            text = NotionClient._rich_text_to_plain_text(rich_text)
            return text or None

        if block_type in {"child_page", "child_database"}:
            title: str | None = payload.get("title")
            return title or None
        if block_type == "equation":
            expression: str | None = payload.get("expression")
            return expression or None
        if block_type in {"bookmark", "embed", "link_preview"}:
            url: str | None = payload.get("url")
            return url or None
        if block_type == "table_row":
            cells: list[Any] = payload.get("cells", [])
            cell_text = [
                NotionClient._rich_text_to_plain_text(cell)
                for cell in cells
                if isinstance(cell, list)
            ]
            joined = " | ".join(text for text in cell_text if text)
            return joined or None

        return None

    @staticmethod
    def _rich_text_to_plain_text(items: list[Any]) -> str:
        """Join ``plain_text`` fragments from a Notion rich-text array."""
        return "".join(
            item.get("plain_text", "") for item in items if isinstance(item, dict)
        ).strip()

    def _call(self, api_method: Any, **kwargs: Any) -> dict[str, Any]:
        """Execute a Notion SDK call with retry and error-translation logic.

        Handles 429 rate-limit responses by sleeping for a fixed interval and retrying
        up to ``settings.notion_max_retries`` times. Both :class:`APIResponseError` and
        :class:`HTTPResponseError` with status 429 go through the same retry path.
        Other errors are translated into :class:`NotionClientError` subclasses.

        Args:
            api_method: A callable from the Notion SDK wrapper.
            **kwargs: Keyword arguments forwarded to ``api_method``.

        Returns:
            The raw response dictionary from the Notion API.
        """
        max_attempts = self._settings.notion_max_retries + 1
        for attempt in range(1, max_attempts + 1):
            try:
                result: dict[str, Any] = api_method(**kwargs)
                return result
            except (APIResponseError, HTTPResponseError) as exc:
                status = exc.status
                if status == _HTTP_TOO_MANY_REQUESTS:
                    if attempt < max_attempts:
                        logger.warning(
                            "Rate limited by Notion API (attempt %d/%d), retrying in %.1fs",
                            attempt,
                            max_attempts,
                            _DEFAULT_RETRY_WAIT_SECONDS,
                        )
                        time.sleep(_DEFAULT_RETRY_WAIT_SECONDS)
                        continue
                    logger.error("Rate limit retries exhausted after %d attempts", max_attempts)
                    raise NotionRateLimitError(
                        f"Rate limit retries exhausted after {max_attempts} attempts"
                    ) from exc
                self._translate_error(exc)

        raise NotionAPIError(  # pragma: no cover
            "Unexpected state: _call loop exited without returning"
        )

    @staticmethod
    def _translate_error(exc: APIResponseError | HTTPResponseError) -> NoReturn:
        """Translate a Notion SDK exception into a domain-specific exception by HTTP status."""
        status = exc.status
        if status == _HTTP_UNAUTHORIZED:
            logger.error("Notion authentication failed: %s", exc)
            raise NotionAuthError(f"Notion authentication failed: {exc}") from exc
        if status in (_HTTP_FORBIDDEN, _HTTP_NOT_FOUND):
            logger.error("Notion resource not found or access denied (status=%d): %s", status, exc)
            raise NotionDatabaseNotFoundError(
                f"Database or data source not found or access denied (status={status}): {exc}"
            ) from exc
        logger.error("Unexpected Notion API error (status=%d): %s", status, exc)
        raise NotionAPIError(f"Unexpected Notion API error (status={status}): {exc}") from exc
