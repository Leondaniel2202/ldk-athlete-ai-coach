"""Shared property parsing helpers for Notion extractors.

Each helper accepts the value of a single Notion property dict (the object under
``raw_page["properties"]["PropertyName"]``) and returns a normalised Python value.
These helpers are intentionally small and cover only the property types used by the
V1 databases.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def _plain_text_from_array(items: list[Any]) -> str:
    """Join ``plain_text`` values from a Notion rich-text or title array."""
    return "".join(item.get("plain_text", "") for item in items)


def get_title(prop: dict[str, Any]) -> str | None:
    """Return plain text from a Notion ``title`` property, or ``None`` if empty."""
    items: list[Any] = prop.get("title", [])
    text = _plain_text_from_array(items)
    return text or None


def get_rich_text(prop: dict[str, Any]) -> str | None:
    """Return plain text from a Notion ``rich_text`` property, or ``None`` if empty."""
    items: list[Any] = prop.get("rich_text", [])
    text = _plain_text_from_array(items)
    return text or None


def get_select(prop: dict[str, Any]) -> str | None:
    """Return the selected option name from a Notion ``select`` property."""
    sel: dict[str, Any] | None = prop.get("select")
    if not sel:
        return None
    return sel.get("name") or None


def get_multi_select(prop: dict[str, Any]) -> list[str]:
    """Return option names from a Notion ``multi_select`` property."""
    items: list[Any] = prop.get("multi_select", [])
    return [item["name"] for item in items if "name" in item]


def get_number(prop: dict[str, Any]) -> float | None:
    """Return the numeric value from a Notion ``number`` property."""
    return prop.get("number")


def get_checkbox(prop: dict[str, Any]) -> bool:
    """Return the boolean value from a Notion ``checkbox`` property."""
    return bool(prop.get("checkbox", False))


def get_date(prop: dict[str, Any]) -> tuple[datetime | None, datetime | None, bool]:
    """Parse a Notion ``date`` property into (start, end, is_datetime).

    ``is_datetime`` is ``True`` when the start value contains a time component
    (i.e. the raw string contains ``"T"``), ``False`` for date-only values.
    """
    date_obj: dict[str, Any] | None = prop.get("date")
    if not date_obj:
        return None, None, False

    start_raw: str | None = date_obj.get("start")
    end_raw: str | None = date_obj.get("end")
    is_datetime = "T" in (start_raw or "")

    start = datetime.fromisoformat(start_raw) if start_raw else None
    end = datetime.fromisoformat(end_raw) if end_raw else None
    return start, end, is_datetime


def get_first_relation(prop: dict[str, Any]) -> str | None:
    """Return the Notion page ID of the first entry in a ``relation`` property."""
    relations: list[Any] = prop.get("relation", [])
    if not relations:
        return None
    return relations[0].get("id")


def get_page_datetime(raw_page: dict[str, Any], key: str) -> datetime | None:
    """Parse a top-level ISO-8601 datetime string from the raw Notion page object."""
    value: str | None = raw_page.get(key)
    if not value:
        return None
    return datetime.fromisoformat(value)
