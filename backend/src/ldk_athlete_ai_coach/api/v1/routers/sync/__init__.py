"""API endpoints for sync-related functionalities."""

from __future__ import annotations

from fastapi import APIRouter

from ldk_athlete_ai_coach.api.v1.routers.sync.notion import router as notion_router

router = APIRouter()

router.include_router(notion_router)
