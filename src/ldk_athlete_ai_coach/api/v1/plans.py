"""Plan endpoints for API v1."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.api.v1.schemas.training import PhaseResponse, PlanResponse
from ldk_athlete_ai_coach.db.repositories.plan_repository import PlanRepository
from ldk_athlete_ai_coach.db.session import get_db_session

router = APIRouter(prefix="/plans", tags=["plans"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: int,
    db: DbSession,
) -> PlanResponse:
    """Retrieve a single plan by ID.

    Args:
        plan_id: Primary key of the plan.
        db: Injected database session.

    Returns:
        PlanResponse: The plan data.

    Raises:
        HTTPException: 404 if the plan does not exist.

    """
    repo = PlanRepository(db)
    plan = repo.get_by_id(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return PlanResponse.model_validate(plan)


@router.get("/{plan_id}/phases", response_model=list[PhaseResponse])
def get_plan_phases(
    plan_id: int,
    db: DbSession,
) -> list[PhaseResponse]:
    """Retrieve all phases belonging to a plan.

    Args:
        plan_id: Primary key of the plan.
        db: Injected database session.

    Returns:
        list[PhaseResponse]: Phases linked to the plan.

    Raises:
        HTTPException: 404 if the plan does not exist.

    """
    repo = PlanRepository(db)
    if repo.get_by_id(plan_id) is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    phases = repo.get_phases(plan_id)
    return [PhaseResponse.model_validate(p) for p in phases]
