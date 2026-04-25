"""Shared Pydantic primitives for extracted Notion schemas."""

from __future__ import annotations

from pydantic import BaseModel


class NotionBaseSchema(BaseModel):
    """Common required identifiers for extracted Notion entities.

    Attributes:
        notion_id: Stable Notion page ID for the source record.
        name: Human-readable title for the record.

    """

    notion_id: str
    name: str
    notion_page_content: str | None = None
