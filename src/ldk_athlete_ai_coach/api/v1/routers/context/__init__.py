"""API endpoints for retrieving training context snapshots."""

from __future__ import annotations

from fastapi import APIRouter

from ldk_athlete_ai_coach.api.v1.routers.context.phase_context import router as phase_context_router
from ldk_athlete_ai_coach.api.v1.routers.context.training_context import (
    router as training_context_router,
)

router = APIRouter()

router.include_router(training_context_router)
router.include_router(phase_context_router)
