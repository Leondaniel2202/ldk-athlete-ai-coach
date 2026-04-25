"""API endpoints for retrieving training context snapshots."""

from __future__ import annotations

from fastapi import APIRouter

from ldk_athlete_ai_coach.api.v1.routers.context.phase_context import router as phase_context_router
from ldk_athlete_ai_coach.api.v1.routers.context.workout_context import (
    router as workout_context_router,
)

router = APIRouter()

router.include_router(phase_context_router)
router.include_router(workout_context_router)
