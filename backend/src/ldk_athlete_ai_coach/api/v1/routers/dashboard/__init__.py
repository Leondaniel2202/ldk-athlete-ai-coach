"""API endpoints for AI-related functionalities."""

from __future__ import annotations

from fastapi import APIRouter

from ldk_athlete_ai_coach.api.v1.routers.dashboard.dashboard import router as dashboard_router

router = APIRouter()

router.include_router(dashboard_router)

__all__ = ["router"]
