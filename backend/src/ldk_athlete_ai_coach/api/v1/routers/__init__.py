"""Version 1 router layer exports."""

from ldk_athlete_ai_coach.api.v1.routers.ai import router as ai_router
from ldk_athlete_ai_coach.api.v1.routers.context import router as context_router
from ldk_athlete_ai_coach.api.v1.routers.resources import router as resources_router
from ldk_athlete_ai_coach.api.v1.routers.sync import router as sync_router
from ldk_athlete_ai_coach.api.v1.routers.system import router as system_router

__all__ = [
    "ai_router",
    "context_router",
    "resources_router",
    "sync_router",
    "system_router",
]
