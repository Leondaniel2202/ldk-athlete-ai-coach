from fastapi import APIRouter

from ldk_athlete_ai_coach.api.v1 import health_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/v1")
