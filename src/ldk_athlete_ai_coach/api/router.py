"""Top-level API router composition."""

from __future__ import annotations

from fastapi import APIRouter

from ldk_athlete_ai_coach.api.v1 import (
    ai_router,
    health_router,
    notion_router,
    phases_router,
    plans_router,
    sessions_router,
    training_context_router,
    workouts_router,
)

api_router = APIRouter()

api_router.include_router(ai_router, prefix="/v1")
api_router.include_router(health_router, prefix="/v1")
api_router.include_router(notion_router, prefix="/v1")
api_router.include_router(phases_router, prefix="/v1")
api_router.include_router(plans_router, prefix="/v1")
api_router.include_router(sessions_router, prefix="/v1")
api_router.include_router(training_context_router, prefix="/v1")
api_router.include_router(workouts_router, prefix="/v1")
