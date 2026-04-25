"""Top-level API router composition."""

from __future__ import annotations

from fastapi import APIRouter

from ldk_athlete_ai_coach.api.v1.routers import (
    ai_router,
    context_router,
    resources_router,
    sync_router,
    system_router,
)

api_router = APIRouter(prefix="/v1")

api_router.include_router(resources_router, prefix="/resources", tags=["resources"])
api_router.include_router(context_router, prefix="/context", tags=["context"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
api_router.include_router(sync_router, prefix="/sync", tags=["sync"])
api_router.include_router(system_router, prefix="/system", tags=["system"])
