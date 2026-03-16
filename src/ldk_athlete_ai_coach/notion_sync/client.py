"""Notion API client wrapper with transparent pagination."""

from __future__ import annotations

from notion_client import Client


class NotionClient:
    """Thin wrapper around the official Notion Python SDK.

    Handles cursor-based pagination so callers always receive the full page list
    for a database query without managing ``next_cursor`` themselves.
    """

    def __init__(self, auth: str) -> None:
        self._client = Client(auth=auth)

    def query_database(self, database_id: str) -> list[dict]:
        """Return every page in a Notion database, following pagination.

        Args:
            database_id: The Notion database UUID to query.

        Returns:
            list[dict]: All page objects returned by the Notion API.
        """
        pages: list[dict] = []
        cursor: str | None = None

        while True:
            kwargs: dict = {"database_id": database_id}
            if cursor:
                kwargs["start_cursor"] = cursor

            response: dict = self._client.databases.query(**kwargs)
            pages.extend(response.get("results", []))

            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

        return pages
