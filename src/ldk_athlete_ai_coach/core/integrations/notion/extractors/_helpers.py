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
    """Join ``plain_text`` values from rich-text style arrays.

    Args:
        items: List of Notion rich-text/title fragments.

    Returns:
        Concatenated plain-text value.

    """
    return "".join(item.get("plain_text", "") for item in items)


def get_title(prop: dict[str, Any]) -> str | None:
    """Extract plain text from a Notion ``title`` property.

    Args:
        prop: Raw Notion property dictionary.

    Returns:
        Extracted title text, or ``None`` when empty.

    """
    items: list[Any] = prop.get("title", [])
    text = _plain_text_from_array(items)
    return text or None


def get_rich_text(prop: dict[str, Any]) -> str | None:
    """Extract plain text from a Notion ``rich_text`` property.

    Args:
        prop: Raw Notion property dictionary.

    Returns:
        Extracted rich-text content, or ``None`` when empty.

    """
    items: list[Any] = prop.get("rich_text", [])
    text = _plain_text_from_array(items)
    return text or None


def get_url(prop: dict[str, Any]) -> str | None:
    """Extract a URL value from a Notion ``url`` property."""
    value: str | None = prop.get("url")
    return value or None


def get_property_by_alias(props: dict[str, Any], *names: str) -> dict[str, Any]:
    """Return the first matching property payload for the provided names.

    Args:
        props: Raw ``properties`` mapping from a Notion page.
        *names: Candidate property names in preferred lookup order.

    Returns:
        The first matching property dictionary, or an empty dictionary when
        none of the names are present.

    """
    for name in names:
        prop = props.get(name)
        if prop is not None:
            return prop
    return {}


def get_place(
    prop: dict[str, Any],
) -> tuple[str | None, str | None, float | None, float | None, str | None]:
    """Extract a Notion ``place`` property into flat scalar values.

    The public Notion API may return ``null`` for unsupported place values, so
    this helper treats missing or unsupported payloads as all-empty.

    Args:
        prop: Raw Notion property dictionary.

    Returns:
        Tuple of ``(name, address, latitude, longitude, google_place_id)``.

    """
    place: dict[str, Any] | None = prop.get("place")
    if not place:
        return None, None, None, None, None

    return (
        place.get("name") or None,
        place.get("address") or None,
        place.get("latitude"),
        place.get("longitude"),
        place.get("google_place_id") or place.get("googlePlaceId") or None,
    )


def get_select(prop: dict[str, Any]) -> str | None:
    """Extract the selected option name from a ``select`` property.

    Args:
        prop: Raw Notion property dictionary.

    Returns:
        Selected option name, or ``None`` when unset.

    """
    sel: dict[str, Any] | None = prop.get("select")
    if not sel:
        return None
    return sel.get("name") or None


def get_multi_select(prop: dict[str, Any]) -> list[str]:
    """Extract selected option names from a ``multi_select`` property.

    Args:
        prop: Raw Notion property dictionary.

    Returns:
        List of selected option names.

    """
    items: list[Any] = prop.get("multi_select", [])
    return [item["name"] for item in items if "name" in item]


def get_number(prop: dict[str, Any]) -> float | None:
    """Extract numeric value from a ``number`` property.

    Args:
        prop: Raw Notion property dictionary.

    Returns:
        Numeric value, or ``None`` when unset.

    """
    return prop.get("number")


def get_formula_number(prop: dict[str, Any]) -> float | None:
    """Extract numeric output from a Notion ``formula`` property."""
    formula: dict[str, Any] | None = prop.get("formula")
    if not formula or formula.get("type") != "number":
        return None
    return formula.get("number")


def get_formula_string(prop: dict[str, Any]) -> str | None:
    """Extract string output from a Notion ``formula`` property."""
    formula: dict[str, Any] | None = prop.get("formula")
    if not formula or formula.get("type") != "string":
        return None
    value: str | None = formula.get("string")
    return value or None


def get_rollup_number(prop: dict[str, Any]) -> float | None:
    """Extract numeric output from a Notion ``rollup`` property."""
    rollup: dict[str, Any] | None = prop.get("rollup")
    if not rollup or rollup.get("type") != "number":
        return None
    return rollup.get("number")


def get_checkbox(prop: dict[str, Any]) -> bool:
    """Extract boolean value from a ``checkbox`` property.

    Args:
        prop: Raw Notion property dictionary.

    Returns:
        Parsed checkbox value.

    """
    return bool(prop.get("checkbox", False))


def _parse_date_object(
    date_obj: dict[str, Any] | None,
) -> tuple[datetime | None, datetime | None, bool]:
    """Parse a raw Notion date object into datetimes and a datetime flag."""
    if not date_obj:
        return None, None, False

    start_raw: str | None = date_obj.get("start")
    end_raw: str | None = date_obj.get("end")
    is_datetime = "T" in (start_raw or "")

    start = datetime.fromisoformat(start_raw) if start_raw else None
    end = datetime.fromisoformat(end_raw) if end_raw else None
    return start, end, is_datetime


def get_date(prop: dict[str, Any]) -> tuple[datetime | None, datetime | None, bool]:
    """Parse a Notion ``date`` property.

    ``is_datetime`` is ``True`` when the start value contains a time component
    (that is, the raw string includes ``"T"``), ``False`` for date-only values.

    Args:
        prop: Raw Notion property dictionary containing a ``date`` object.

    Returns:
        A tuple of ``(start, end, is_datetime)`` where ``start`` and ``end``
        are parsed datetimes when present.

    """
    return _parse_date_object(prop.get("date"))


def get_rollup_date(prop: dict[str, Any]) -> tuple[datetime | None, datetime | None, bool]:
    """Parse date output from a Notion ``rollup`` property."""
    rollup: dict[str, Any] | None = prop.get("rollup")
    if not rollup or rollup.get("type") != "date":
        return None, None, False
    return _parse_date_object(rollup.get("date"))


def get_first_relation(prop: dict[str, Any]) -> str | None:
    """Extract the first related Notion page ID from a ``relation`` property.

    Args:
        prop: Raw Notion property dictionary.

    Returns:
        First relation page ID, or ``None`` when no relations exist.

    """
    relations: list[Any] = prop.get("relation", [])
    if not relations:
        return None
    return relations[0].get("id")


def get_page_datetime(raw_page: dict[str, Any], key: str) -> datetime | None:
    """Parse a top-level ISO-8601 datetime field from a raw Notion page.

    Args:
        raw_page: Raw page payload from the Notion API.
        key: Top-level datetime key (for example ``created_time``).

    Returns:
        Parsed datetime value, or ``None`` when missing.

    """
    value: str | None = raw_page.get(key)
    if not value:
        return None
    return datetime.fromisoformat(value)
