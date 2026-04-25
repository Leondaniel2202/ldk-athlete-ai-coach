"""API endpoints for system-related functionalities."""

from __future__ import annotations

from fastapi import APIRouter

from ldk_athlete_ai_coach.api.v1.routers.system.health import router as health_router

router = APIRouter(tags=["system"])

router.include_router(health_router)
