"""Aggregate current training context from the local database."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from ldk_athlete_ai_coach.api.v1.schemas.training import (
    AdherenceSummaryResponse,
    CurrentTrainingContextResponse,
    PhaseResponse,
    PlanResponse,
    RecentWorkoutContextResponse,
    SessionResponse,
    TrainingContextMetadataResponse,
    TrainingContextResponse,
    WorkoutDetailResponse,
)
from ldk_athlete_ai_coach.db.models.training import Phase, TrackedSession
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.plan_repository import PlanRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository


class TrainingContextService:
    """Build the workout-centric current training context response."""

    def __init__(
        self,
        plan_repository: PlanRepository,
        phase_repository: PhaseRepository,
        workout_repository: WorkoutRepository,
        session_repository: SessionRepository,
    ) -> None:
        self._plan_repository = plan_repository
        self._phase_repository = phase_repository
        self._workout_repository = workout_repository
        self._session_repository = session_repository

    def get_current_context(self, now: datetime | None = None) -> TrainingContextResponse:
        """Return the current aggregated training context."""
        as_of = now or datetime.now(tz=UTC)
        cutoff = as_of - timedelta(days=7)
        data_gaps: list[str] = []

        plan = self._plan_repository.get_active_for_datetime(as_of)
        if plan is None:
            plan = self._plan_repository.get_latest()
            if plan is None:
                data_gaps.append("No plan data is available.")
            else:
                data_gaps.append(
                    "No active plan matched the current date; using the latest available plan instead."
                )

        phase = self._select_phase(
            plan_id=plan.id if plan is not None else None,
            now=as_of,
            data_gaps=data_gaps,
        )

        planned_workouts: list[WorkoutDetailResponse] = []
        if phase is not None:
            missing_planned_dates = self._workout_repository.count_missing_scheduled_date_for_phase(
                phase.id
            )
            if missing_planned_dates:
                data_gaps.append(
                    self._count_message(
                        missing_planned_dates,
                        singular="workout in the current phase is missing date_start and was excluded from planned context.",
                        plural="workouts in the current phase are missing date_start and were excluded from planned context.",
                    )
                )
            planned_workouts = [
                WorkoutDetailResponse.model_validate(workout)
                for workout in self._workout_repository.get_upcoming_for_phase(phase.id, as_of)
            ]

        recent_workout_entities = self._workout_repository.get_recent_by_effective_date(cutoff, as_of)
        recent_sessions = self._session_repository.get_for_workout_ids(
            [workout.id for workout in recent_workout_entities]
        )
        sessions_by_workout = self._group_sessions_by_workout(recent_sessions)
        recent_workouts = [
            RecentWorkoutContextResponse(
                workout=WorkoutDetailResponse.model_validate(workout),
                tracked_sessions=[
                    SessionResponse.model_validate(session)
                    for session in sessions_by_workout.get(workout.id, [])
                ],
            )
            for workout in recent_workout_entities
        ]

        adherence_workouts = self._workout_repository.get_scheduled_within_window(cutoff, as_of)
        adherence_sessions = self._session_repository.get_for_workout_ids(
            [workout.id for workout in adherence_workouts]
        )
        completed_workout_ids = {
            session.workout_id for session in adherence_sessions if session.workout_id is not None
        }
        skipped_workouts = sum(
            1
            for workout in adherence_workouts
            if workout.skipped or (workout.status or "").casefold() == "skipped"
        )
        planned_count = len(adherence_workouts)
        completed_count = sum(1 for workout in adherence_workouts if workout.id in completed_workout_ids)

        unlinked_recent_sessions = self._session_repository.get_recent_unlinked(cutoff, as_of)
        if unlinked_recent_sessions:
            data_gaps.append(
                self._count_message(
                    len(unlinked_recent_sessions),
                    singular="recent tracked session is not linked to a workout.",
                    plural="recent tracked sessions are not linked to a workout.",
                )
            )

        return TrainingContextResponse(
            metadata=TrainingContextMetadataResponse(as_of_date=as_of.date(), timezone="UTC"),
            current=CurrentTrainingContextResponse(
                plan=PlanResponse.model_validate(plan) if plan is not None else None,
                phase=PhaseResponse.model_validate(phase) if phase is not None else None,
                current_phase_week=self._compute_phase_week(phase, as_of.date()),
            ),
            planned_workouts=planned_workouts,
            recent_workouts=recent_workouts,
            adherence=AdherenceSummaryResponse(
                planned_workouts=planned_count,
                completed_workouts=completed_count,
                skipped_workouts=skipped_workouts,
                completion_ratio=(completed_count / planned_count) if planned_count else None,
            ),
            data_gaps=data_gaps,
        )

    def _select_phase(
        self,
        plan_id: int | None,
        now: datetime,
        data_gaps: list[str],
    ) -> Phase | None:
        """Return the current phase for the selected plan, recording gaps as needed."""
        if plan_id is None:
            return None

        phase = self._phase_repository.get_active_for_plan(plan_id, now)
        if phase is not None:
            return phase

        phase = self._phase_repository.get_latest_for_plan(plan_id)
        if phase is None:
            data_gaps.append("No phase data is available for the selected plan.")
            return None

        data_gaps.append(
            "No active phase matched the current date; using the latest phase for the selected plan instead."
        )
        return phase

    @staticmethod
    def _compute_phase_week(phase: Phase | None, as_of_date: date) -> int | None:
        """Derive the current phase week from the phase start date."""
        if phase is None or phase.timeframe_start is None:
            return None
        days_since_start = (as_of_date - phase.timeframe_start.date()).days
        return max((days_since_start // 7) + 1, 1)

    @staticmethod
    def _group_sessions_by_workout(
        sessions: list[TrackedSession],
    ) -> dict[int, list[TrackedSession]]:
        """Group sessions by workout ID while preserving query order."""
        grouped: dict[int, list[TrackedSession]] = {}
        for session in sessions:
            if session.workout_id is None:
                continue
            grouped.setdefault(session.workout_id, []).append(session)
        return grouped

    @staticmethod
    def _count_message(count: int, *, singular: str, plural: str) -> str:
        """Return a deterministic count-prefixed gap message."""
        suffix = singular if count == 1 else plural
        return f"{count} {suffix}"
