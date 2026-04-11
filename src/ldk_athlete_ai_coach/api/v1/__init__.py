"""Version 1 API router exports."""

from ldk_athlete_ai_coach.api.v1.health import router as health_router
from ldk_athlete_ai_coach.api.v1.notion import router as notion_router

__all__ = ["health_router", "notion_router"]
