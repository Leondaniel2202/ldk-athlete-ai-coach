"""Notion API client foundation.

This module provides a low-level, reusable Notion client built on top of the official
``notion-client`` SDK. It handles authentication, database queries, automatic pagination,
basic rate-limit handling, and structured logging.

Higher-level components such as extractors, mappers, and sync services should import and
use :class:`NotionClient` rather than interacting with the SDK directly.

Typical usage::

    from ldk_athlete_ai_coach.core.integrations.notion.client import NotionClient
    from ldk_athlete_ai_coach.core.config import get_settings

    client = NotionClient(get_settings())

    # Retrieve raw database metadata
    metadata = client.get_database(database_id="<uuid>")

    # Fetch a single page of query results
    page = client.query_database(database_id="<uuid>")

    # Iterate over all individual entries across all pages
    for entry in client.iter_database_entries(database_id="<uuid>"):
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
    """Raised when the requested database cannot be found or accessed."""


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


# ---------------------------------------------------------------------------
# NotionClient
# ---------------------------------------------------------------------------


class NotionClient:
    """Low-level Notion API client.

    Wraps the official ``notion-client`` SDK to provide:

    * Authenticated access using the configured ``NOTION_API_KEY``.
    * Database metadata retrieval (:meth:`get_database`).
    * Single-page database queries (:meth:`query_database`).
    * Full paginated iteration (:meth:`iter_database_entries`).
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
        )
        logger.debug("NotionClient initialised (timeout=%ds)", settings.notion_timeout_seconds)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_database(self, database_id: str) -> dict[str, Any]:
        """Retrieve metadata for a Notion database.

        Args:
            database_id: The UUID of the target Notion database.

        Returns:
            Raw Notion database object as returned by the API.

        Raises:
            NotionAuthError: If credentials are invalid or missing.
            NotionDatabaseNotFoundError: If the database cannot be found or accessed.
            NotionAPIError: For any other unexpected API error.
        """
        logger.debug("Fetching database metadata for database_id=%s", database_id)
        return self._call(self._client.databases.retrieve, database_id=database_id)

    def query_database(
        self,
        database_id: str,
        start_cursor: str | None = None,
    ) -> dict[str, Any]:
        """Query a Notion database and return a single page of results.

        Args:
            database_id: The UUID of the target Notion database.
            start_cursor: Optional pagination cursor returned by a previous query.

        Returns:
            Raw Notion query response (``results``, ``has_more``, ``next_cursor``, …).

        Raises:
            NotionAuthError: If credentials are invalid or missing.
            NotionDatabaseNotFoundError: If the database cannot be found or accessed.
            NotionAPIError: For any other unexpected API error.
        """
        logger.debug(
            "Querying database_id=%s start_cursor=%s page_size=%d",
            database_id,
            start_cursor,
            self._settings.notion_page_size,
        )
        kwargs: dict[str, Any] = {
            "database_id": database_id,
            "page_size": self._settings.notion_page_size,
        }
        if start_cursor is not None:
            kwargs["start_cursor"] = start_cursor

        response: dict[str, Any] = self._call(self._client.databases.query, **kwargs)
        result_count = len(response.get("results", []))
        logger.debug("Fetched %d result(s) from database_id=%s", result_count, database_id)
        return response

    def iter_database_entries(self, database_id: str) -> Iterator[dict[str, Any]]:
        """Iterate over every individual entry in a database, handling pagination.

        Follows ``next_cursor`` across all response pages and yields each raw Notion
        entry (page object) one at a time. Callers do not need to manage cursors or
        loop over response pages themselves.

        Args:
            database_id: The UUID of the target Notion database.

        Yields:
            Individual raw Notion page objects (database entries) from the query results.

        Raises:
            NotionAuthError: If credentials are invalid or missing.
            NotionDatabaseNotFoundError: If the database cannot be found or accessed.
            NotionAPIError: For any other unexpected API error.
        """
        cursor: str | None = None
        total = 0

        while True:
            response = self.query_database(database_id, start_cursor=cursor)
            results: list[dict[str, Any]] = response.get("results", [])
            total += len(results)
            yield from results

            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

        logger.info(
            "Finished paginated query for database_id=%s total_results=%d",
            database_id,
            total,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _call(self, api_method: Any, **kwargs: Any) -> dict[str, Any]:
        """Execute a Notion SDK call with retry and error-translation logic.

        Handles 429 rate-limit responses by sleeping for a fixed interval and retrying
        up to ``settings.notion_max_retries`` times. Both :class:`APIResponseError` and
        :class:`HTTPResponseError` with status 429 go through the same retry path.
        Other errors are translated into :class:`NotionClientError` subclasses.

        Args:
            api_method: A callable from the Notion SDK (e.g. ``client.databases.query``).
            **kwargs: Keyword arguments forwarded to ``api_method``.

        Returns:
            The raw response dictionary from the Notion API.

        Raises:
            NotionAuthError: On HTTP 401.
            NotionDatabaseNotFoundError: On HTTP 403 or 404.
            NotionRateLimitError: When 429 retries are exhausted.
            NotionAPIError: For any other API / HTTP error.
        """
        # Total attempts = 1 initial + notion_max_retries retries.
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
                if isinstance(exc, APIResponseError):
                    self._handle_api_error(exc)
                raise NotionAPIError(f"Unexpected HTTP error: {exc}") from exc

        # Should not be reached, but satisfies static analysis.
        raise NotionAPIError(  # pragma: no cover
            "Unexpected state: _call loop exited without returning"
        )

    @staticmethod
    def _handle_api_error(exc: APIResponseError) -> NoReturn:
        """Translate an :class:`APIResponseError` into a domain-specific exception.

        Does not handle 429 — rate-limit retries are managed by :meth:`_call` before
        this method is invoked.

        Args:
            exc: The original SDK exception.

        Raises:
            NotionAuthError: On 401 status.
            NotionDatabaseNotFoundError: On 403 or 404 status.
            NotionAPIError: For all other status codes.
        """
        status = exc.status
        if status == _HTTP_UNAUTHORIZED:
            logger.error("Notion authentication failed: %s", exc)
            raise NotionAuthError(f"Notion authentication failed: {exc}") from exc
        if status in (_HTTP_FORBIDDEN, _HTTP_NOT_FOUND):
            logger.error("Notion database not found or access denied (status=%d): %s", status, exc)
            raise NotionDatabaseNotFoundError(
                f"Database not found or access denied (status={status}): {exc}"
            ) from exc
        logger.error("Unexpected Notion API error (status=%d): %s", status, exc)
        raise NotionAPIError(f"Unexpected Notion API error (status={status}): {exc}") from exc
