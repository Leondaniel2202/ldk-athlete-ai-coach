"""API endpoints for AI-related functionalities."""

from __future__ import annotations

from fastapi import APIRouter

from ldk_athlete_ai_coach.api.v1.routers.ai.analysis import router as analysis_router

router = APIRouter()

router.include_router(analysis_router)

__all__ = ["router"]
