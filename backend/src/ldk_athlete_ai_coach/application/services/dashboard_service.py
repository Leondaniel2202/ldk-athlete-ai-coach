"""This module contains the DashboardService class, which is responsible
for fetching and aggregating data for the dashboard overview."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from ldk_athlete_ai_coach.api.v1.schemas.dashboard import (
    DashboardDataResponse,
    OverviewItemResponse,
)
from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.plans import PlanSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.workouts import (
    WorkoutSummaryResponse,
)
from ldk_athlete_ai_coach.db.models.training import Phase, Plan, Workout
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.plan_repository import PlanRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.domain.enums.phase import get_phase_type_details
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus
from ldk_athlete_ai_coach.utils.date_utils import get_week_start_for_date


class DashboardService:
    """Service layer for fetching and aggregating data for the dashboard overview.

    This service is responsible for orchestrating calls to the various repositories to gather the
    necessary data for the dashboard, and then transforming that data into the appropriate
    response schemas for the API layer. It encapsulates the business logic for determining the
    current training context, summarizing workout execution, and preparing the high-level overview /
    items that are displayed on the dashboard.
    """

    def __init__(
        self,
        plan_repository: PlanRepository,
        phase_repository: PhaseRepository,
        workout_repository: WorkoutRepository,
        session_repository: SessionRepository,
    ) -> None:
        """Initialize the service with all required repositories.

        Args:
            plan_repository: Repository for plan lookups.
            phase_repository: Repository for phase lookups.
            workout_repository: Repository for workout lookups.
            session_repository: Repository for tracked-session lookups.
        """
        self._plan_repository: PlanRepository = plan_repository
        self._phase_repository: PhaseRepository = phase_repository
        self._workout_repository: WorkoutRepository = workout_repository
        self._session_repository: SessionRepository = session_repository

    def get_dashboard(self) -> DashboardDataResponse:
        """Fetch and aggregate data for the dashboard overview."""
        as_of: datetime = datetime.now(tz=UTC)
        week_start_date: datetime = get_week_start_for_date(date=as_of)
        plan: Plan | None = self._plan_repository.get_active_for_datetime(now=as_of)
        phase: Phase | None = self._phase_repository.get_active_for_datetime(now=as_of)
        workouts: list[Workout] = self._workout_repository.list_within_planned_week(
            week_start_date=week_start_date
        )

        category_counts: dict[str, int] = {}
        for workout in workouts:
            key = workout.category or "Uncategorised"
            category_counts[key] = category_counts.get(key, 0) + 1

        done_count = sum(1 for w in workouts if w.status == WorkoutStatus.DONE)
        skipped_count = sum(1 for w in workouts if w.status == WorkoutStatus.SKIPPED)
        open_count = sum(1 for w in workouts if w.status == WorkoutStatus.OPEN)
        planned_weekly_load: float | Literal[0] = sum(
            w.planned_training_load for w in workouts if w.planned_training_load
        )

        overview_items = [
            OverviewItemResponse(
                label="Training focus",
                value=phase.phase_type if phase else None,
                detail=get_phase_type_details(phase.phase_type).description
                if phase and phase.phase_type
                else None,
            ),
            OverviewItemResponse(
                label="This Week",
                value=f"{len(workouts)} Workout{'s' if len(workouts) != 1 else ''}",
                detail=", ".join(
                    f"{count} {category} {'workout' if count == 1 else 'workouts'}"
                    for category, count in sorted(category_counts.items())
                ),
            ),
            OverviewItemResponse(
                label="Execution",
                value="On Track" if skipped_count == 0 else "Needs Attention",
                detail=f"{done_count} done, {skipped_count} skipped, {open_count} open",
            ),
            OverviewItemResponse(
                label="Planned Training Load",
                value=str(planned_weekly_load),
                detail="Weekly load planned across all workouts with training load data",
            ),
        ]

        weekly_outlook = [WorkoutSummaryResponse.model_validate(workout) for workout in workouts]

        return DashboardDataResponse(
            athlete_name="Leon",
            summary=(
                "This is the starting point for reviewing the current training situation"
                " before moving into planning, analysis, or coaching workflows."
            ),
            next_action=(
                "Select a workout from the weekly outlook to review details,"
                " track a session, or log notes."
            ),
            overview=overview_items,
            current_plan=PlanSummaryResponse.model_validate(plan) if plan else None,
            current_phase=PhaseSummaryResponse.model_validate(phase) if phase else None,
            weekly_outlook=weekly_outlook,
        )
