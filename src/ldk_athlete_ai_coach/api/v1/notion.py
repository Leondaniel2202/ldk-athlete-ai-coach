"""Public Notion sync endpoints for API v1."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ldk_athlete_ai_coach.core.config import get_settings
from ldk_athlete_ai_coach.core.integrations.notion.client import (
    NotionAPIError,
    NotionAuthError,
    NotionClient,
    NotionDatabaseNotFoundError,
    NotionRateLimitError,
)
from ldk_athlete_ai_coach.core.integrations.notion.sync_service import (
    NotionSyncError,
    NotionSyncService,
    SyncResult,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["notion"])


class NotionSyncEntitySummary(BaseModel):
    """Public API shape for a single synced entity summary."""

    entity: str
    fetched: int
    success: int
    failed: int


class NotionSyncSummary(BaseModel):
    """Public API shape for the aggregate full-sync summary."""

    total_fetched: int
    total_success: int
    total_failed: int
    results: list[NotionSyncEntitySummary]


def _build_sync_summary(results: list[SyncResult]) -> NotionSyncSummary:
    """Convert service sync results into an API-safe summary payload."""
    return NotionSyncSummary(
        total_fetched=sum(result.fetched for result in results),
        total_success=sum(result.success for result in results),
        total_failed=sum(result.failed for result in results),
        results=[
            NotionSyncEntitySummary(
                entity=result.entity,
                fetched=result.fetched,
                success=result.success,
                failed=result.failed,
            )
            for result in results
        ],
    )


@router.post("/notion/sync", response_model=NotionSyncSummary)
async def sync_notion(
    hard_fail: bool = Query(
        default=False,
        description="When true, abort sync immediately on first entity failure.",
    ),
) -> NotionSyncSummary | JSONResponse:
    """Run a full blocking Notion sync and return the sync summary."""
    settings = get_settings()
    client = NotionClient(settings)
    service = NotionSyncService(client, settings, hard_fail=hard_fail)

    try:
        results = service.sync_all()
    except NotionSyncError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=exc.to_detail(),
        ) from exc
    except NotionRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except (NotionAuthError, NotionDatabaseNotFoundError, NotionAPIError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during full Notion sync")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during full Notion sync",
        ) from exc

    summary = _build_sync_summary(results)
    if summary.total_failed > 0:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=summary.model_dump(),
        )
    return summary
