"""Notion extraction layer.

Extractors convert raw Notion page objects (``dict[str, Any]``) returned by the
:class:`~ldk_athlete_ai_coach.core.integrations.notion.client.NotionClient` into
typed Pydantic models defined in the ``schemas`` package.
"""

from __future__ import annotations


class NotionExtractionError(Exception):
    """Raised when a raw Notion page cannot be parsed into a typed extraction model.

    Wraps low-level errors (``KeyError``, ``TypeError``, ``ValueError``) so that
    callers receive a predictable, domain-specific exception rather than a generic
    Python built-in.
    """
