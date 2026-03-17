"""Notion API client for authenticated, paginated database reads.

Usage by higher-level sync components::

    from ldk_athlete_ai_coach.core.config import get_settings
    from ldk_athlete_ai_coach.core.integrations.notion.client import NotionClient

    client = NotionClient.from_settings(get_settings())

    # Fetch all pages from a database (pagination handled automatically)
    pages = client.query_all_pages(settings.notion_phase_db_id)

    # Or fetch one page at a time with a cursor
    result = client.query_database(database_id, start_cursor=None)

This layer returns raw Notion API responses unchanged. Extraction, mapping, and
persistence are handled by higher layers built on top of this client.
"""

import logging
import time
from typing import Any

import httpx

from ldk_athlete_ai_coach.core.config import Settings

logger = logging.getLogger(__name__)

_NOTION_API_BASE = "https://api.notion.com/v1"
_NOTION_VERSION = "2022-06-28"


class NotionError(Exception):
    """Base exception for Notion client errors."""


class NotionConfigError(NotionError):
    """Raised when required Notion configuration is missing."""


class NotionAuthError(NotionError):
    """Raised when the Notion API rejects the API key."""


class NotionDatabaseError(NotionError):
    """Raised when a database is not found or access is denied."""


class NotionRateLimitError(NotionError):
    """Raised when rate-limit retries are exhausted."""


class NotionAPIError(NotionError):
    """Raised for unexpected Notion API responses."""


class NotionClient:
    """Low-level client for the Notion API.

    Handles authentication, database queries, pagination, and basic rate-limit
    retries. Does not perform extraction, mapping, or persistence.
    """

    def __init__(
        self,
        api_key: str,
        *,
        page_size: int = 100,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self._page_size = page_size
        self._max_retries = max_retries
        self._http = httpx.Client(
            base_url=_NOTION_API_BASE,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Notion-Version": _NOTION_VERSION,
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    @classmethod
    def from_settings(cls, settings: Settings) -> "NotionClient":
        """Instantiate a NotionClient from application settings.

        Raises:
            NotionConfigError: If NOTION_API_KEY is not configured.
        """
        if not settings.notion_api_key:
            raise NotionConfigError("NOTION_API_KEY is not configured")
        return cls(
            api_key=settings.notion_api_key,
            page_size=settings.notion_page_size,
            timeout=settings.notion_timeout,
            max_retries=settings.notion_max_retries,
        )

    def get_database(self, database_id: str) -> dict[str, Any]:
        """Retrieve metadata for a Notion database.

        Args:
            database_id: The Notion database ID.

        Returns:
            Raw Notion database object.
        """
        logger.debug("Fetching database metadata", extra={"database_id": database_id})
        return self._request("GET", f"/databases/{database_id}")

    def query_database(
        self,
        database_id: str,
        start_cursor: str | None = None,
    ) -> dict[str, Any]:
        """Query one page of results from a Notion database.

        Args:
            database_id: The Notion database ID.
            start_cursor: Pagination cursor from a previous response.

        Returns:
            Raw Notion query response containing ``results`` and pagination fields.
        """
        logger.debug(
            "Querying database page",
            extra={"database_id": database_id, "start_cursor": start_cursor},
        )
        body: dict[str, Any] = {"page_size": self._page_size}
        if start_cursor:
            body["start_cursor"] = start_cursor

        response = self._request("POST", f"/databases/{database_id}/query", json=body)
        logger.debug(
            "Page fetched",
            extra={
                "database_id": database_id,
                "result_count": len(response.get("results", [])),
                "has_more": response.get("has_more", False),
            },
        )
        return response

    def query_all_pages(self, database_id: str) -> list[dict[str, Any]]:
        """Fetch all pages from a Notion database, handling pagination automatically.

        Args:
            database_id: The Notion database ID.

        Returns:
            List of all raw Notion page objects from the database.
        """
        logger.info("Starting full database query", extra={"database_id": database_id})
        all_results: list[dict[str, Any]] = []
        cursor: str | None = None

        while True:
            response = self.query_database(database_id, start_cursor=cursor)
            all_results.extend(response.get("results", []))
            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

        logger.info(
            "Database query complete",
            extra={"database_id": database_id, "total_results": len(all_results)},
        )
        return all_results

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Execute an HTTP request with retry on rate limiting.

        Raises:
            NotionAuthError: On HTTP 401.
            NotionDatabaseError: On HTTP 403 or 404.
            NotionRateLimitError: On HTTP 429 after all retries are exhausted.
            NotionAPIError: On any other unexpected response or request failure.
        """
        for attempt in range(self._max_retries + 1):
            try:
                response = self._http.request(method, path, **kwargs)
            except httpx.RequestError as exc:
                raise NotionAPIError(f"Request to Notion failed: {exc}") from exc

            if response.status_code == 200:
                return response.json()

            if response.status_code == 401:
                raise NotionAuthError("Notion API key is invalid or missing")

            if response.status_code in (403, 404):
                raise NotionDatabaseError(
                    f"Database not found or access denied (HTTP {response.status_code})"
                )

            if response.status_code == 429:
                if attempt < self._max_retries:
                    retry_after = float(response.headers.get("Retry-After", 1))
                    logger.warning(
                        "Rate limited by Notion, retrying",
                        extra={"attempt": attempt + 1, "retry_after": retry_after},
                    )
                    time.sleep(retry_after)
                    continue
                raise NotionRateLimitError("Rate limit retries exhausted")

            raise NotionAPIError(f"Unexpected Notion API response: {response.status_code}")

        raise NotionRateLimitError("Rate limit retries exhausted")  # pragma: no cover
