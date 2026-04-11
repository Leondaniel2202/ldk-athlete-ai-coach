"""Version 1 API router exports."""

from ldk_athlete_ai_coach.api.v1.health import router as health_router
from ldk_athlete_ai_coach.api.v1.notion import router as notion_router
from ldk_athlete_ai_coach.api.v1.phases import router as phases_router
from ldk_athlete_ai_coach.api.v1.plans import router as plans_router
from ldk_athlete_ai_coach.api.v1.sessions import router as sessions_router
from ldk_athlete_ai_coach.api.v1.workouts import router as workouts_router

__all__ = [
    "health_router",
    "notion_router",
    "phases_router",
    "plans_router",
    "sessions_router",
    "workouts_router",
]
