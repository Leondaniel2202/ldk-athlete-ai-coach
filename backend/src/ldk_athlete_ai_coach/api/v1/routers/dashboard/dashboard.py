from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends
from typing import Annotated
from ldk_athlete_ai_coach.api.v1.schemas.dashboard import DashboardDataResponse
from ldk_athlete_ai_coach.application.services.dashboard_service import DashboardService
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.plan_repository import PlanRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.db.session import get_db_session

router = APIRouter()

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/overview", response_model=DashboardDataResponse)
def get_dashboard_data(
    db: DbSession,
) -> DashboardDataResponse:
    """Fetch and aggregate data for the dashboard overview."""
    service = DashboardService(
        plan_repository=PlanRepository(db),
        phase_repository=PhaseRepository(db),
        workout_repository=WorkoutRepository(db),
        session_repository=SessionRepository(db),
    )
    return service.get_dashboard()
