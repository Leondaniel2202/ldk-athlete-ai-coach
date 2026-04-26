"""API endpoints for resource-related functionalities."""

from __future__ import annotations

from fastapi import APIRouter

from ldk_athlete_ai_coach.api.v1.routers.resources.phases import router as phases_router
from ldk_athlete_ai_coach.api.v1.routers.resources.plans import router as plans_router
from ldk_athlete_ai_coach.api.v1.routers.resources.sessions import router as sessions_router
from ldk_athlete_ai_coach.api.v1.routers.resources.workouts import router as workouts_router

router = APIRouter()

router.include_router(plans_router)
router.include_router(phases_router)
router.include_router(sessions_router)
router.include_router(workouts_router)
