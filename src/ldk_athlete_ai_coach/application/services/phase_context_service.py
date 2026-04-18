"""Aggregate current phase context from the local database."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, datetime
from typing import cast

from ldk_athlete_ai_coach.api.v1.schemas.adherence import WorkoutAdherenceSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.common import ContextMetadataResponse
from ldk_athlete_ai_coach.api.v1.schemas.metrics import TrainingMetricsResponse
from ldk_athlete_ai_coach.api.v1.schemas.phase_context import (
    PhaseContextResponse,
    PhaseWeekContextMetadataResponse,
    PhaseWeekContextResponse,
)
from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseResponse, PhaseSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.plans import PlanSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.sessions import SessionResponse
from ldk_athlete_ai_coach.api.v1.schemas.workouts import (
    WorkoutContentResponse,
    WorkoutDetailResponse,
)
from ldk_athlete_ai_coach.db.models.training import Phase, TrackedSession, Workout
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.domain.calculators.status_calculator import StatusCalculator
from ldk_athlete_ai_coach.domain.calculators.training_metrics_calculator import (
    TrainingMetricsCalculator,
)
from ldk_athlete_ai_coach.domain.enums.status import PhaseStatus, WorkoutStatus
from ldk_athlete_ai_coach.utils.date_utils import (
    get_phase_week_number_for_date,
    get_week_end_for_date,
)


class PhaseContextService:
    """Build the phase-centric training context response.

    Orchestrates repository calls, status calculations, and data-quality checks
    to produce a ``PhaseContextResponse`` for a single training phase.
    """

    def __init__(
        self,
        phase_repository: PhaseRepository,
        workout_repository: WorkoutRepository,
        session_repository: SessionRepository,
    ) -> None:
        """Initialize the service with all required repositories.

        Args:
            plan_repository: Repository for training plan lookups.
            phase_repository: Repository for training phase lookups.
            workout_repository: Repository for workout lookups.
            session_repository: Repository for tracked-session lookups.
        """
        self._phase_repository: PhaseRepository = phase_repository
        self._workout_repository: WorkoutRepository = workout_repository
        self._session_repository: SessionRepository = session_repository
        self._status_calculator = StatusCalculator()
        self._metrics_calculator = TrainingMetricsCalculator()

    @staticmethod
    def _count_message(count: int, *, singular: str, plural: str) -> str:
        """Format a human-readable count message using correct singular or plural form.

        Args:
            count: The numeric count to include in the message.
            singular: Message suffix used when count is exactly 1.
            plural: Message suffix used when count is not 1.

        Returns:
            A string of the form ``"{count} {suffix}"``.
        """
        suffix = singular if count == 1 else plural
        return f"{count} {suffix}"

    @staticmethod
    def _count_workouts_by_status(workouts: list[Workout]) -> dict[WorkoutStatus, int]:
        """Count workouts grouped by their lifecycle status.

        Every ``WorkoutStatus`` enum member is guaranteed to appear as a key,
        defaulting to zero when no workouts hold that status.

        Args:
            workouts: Workout ORM instances to tally.

        Returns:
            A mapping of each ``WorkoutStatus`` to its count.
        """
        counts = Counter(w.status for w in workouts)

        return {status: counts.get(status, 0) for status in WorkoutStatus}

    @staticmethod
    def _can_check_unlinked_sessions(
        *,
        phase: Phase,
        phase_status: PhaseStatus,
    ) -> bool:
        """Return whether unlinked-session detection is possible for a phase.

        Detection requires the phase to be active or past and have a fully
        bounded timeframe so that a session window can be derived.

        Args:
            phase: The training phase being evaluated.
            phase_status: Pre-calculated lifecycle status of the phase.

        Returns:
            ``True`` when unlinked-session detection can meaningfully run.
        """
        return (
            phase_status in {PhaseStatus.ACTIVE, PhaseStatus.PAST}
            and phase.timeframe_start is not None
            and phase.timeframe_end is not None
        )

    def _build_open_workout_content_responses(
        self,
        all_workouts: list[Workout],
    ) -> list[WorkoutContentResponse]:
        """Build content responses for all open (upcoming) workouts in a phase.

        Args:
            all_workouts: Full list of workout ORM instances for the phase.

        Returns:
            Validated ``WorkoutContentResponse`` objects for open workouts only.
        """
        return [
            WorkoutContentResponse.model_validate(workout)
            for workout in all_workouts
            if workout.status == WorkoutStatus.OPEN
        ]

    def _build_done_workout_detail_responses(
        self,
        all_workouts: list[Workout],
    ) -> list[WorkoutDetailResponse]:
        """Build detailed responses for completed workouts, including linked sessions.

        Fetches tracked sessions in a single batched query and groups them
        by workout, then assembles a ``WorkoutDetailResponse`` for each
        completed workout.

        Args:
            all_workouts: Full list of workout ORM instances for the phase.

        Returns:
            Validated ``WorkoutDetailResponse`` objects for done workouts,
            each populated with its associated tracked sessions.
        """
        done_workouts = [
            workout for workout in all_workouts if workout.status == WorkoutStatus.DONE
        ]

        if not done_workouts:
            return []

        workout_ids = [workout.id for workout in done_workouts]
        tracked_sessions = self._session_repository.list_by_workout_ids(workout_ids=workout_ids)

        sessions_by_workout_id: dict[int, list[TrackedSession]] = defaultdict(list)
        for session in tracked_sessions:
            if session.workout_id is not None:
                sessions_by_workout_id[session.workout_id].append(session)

        responses: list[WorkoutDetailResponse] = []
        for workout in done_workouts:
            base = WorkoutContentResponse.model_validate(workout)

            responses.append(
                WorkoutDetailResponse(
                    **base.model_dump(),
                    tracked_sessions=[
                        SessionResponse.model_validate(session)
                        for session in sessions_by_workout_id.get(workout.id, [])
                    ],
                )
            )

        return responses

    def _build_training_metrics_response(
        self,
        workouts: list[Workout],
        timeframe_start: datetime | None,
        timeframe_end: datetime | None,
    ) -> TrainingMetricsResponse:
        """Calculate training metrics for a list of workouts.

        Args:
            workouts: List of workout ORM instances for one week.
            timeframe_start: Start date of the timeframe for which metrics are being calculated.
                Can be ``None`` if not defined.
            timeframe_end: End date of the timeframe for which metrics are being calculated.
                Can be ``None`` if not defined.

        Returns:
            A ``TrainingMetricsResponse`` containing calculated metrics.

        """
        return TrainingMetricsResponse(
            timeframe_start=timeframe_start.date() if timeframe_start else None,
            timeframe_end=timeframe_end.date() if timeframe_end else None,
            training_metrics=self._metrics_calculator.calculate(workouts=workouts),
        )

    def get_specific_phase_context(self, phase_id: int) -> PhaseContextResponse:
        """Build and return the full context snapshot for a specific training phase.

        Args:
            phase_id: Primary key of the phase to build context for.

        Returns:
            A fully populated ``PhaseContextResponse``.

        Raises:
            ValueError: If no phase with the given ``phase_id`` exists.
        """
        as_of = datetime.now(tz=UTC)

        phase: Phase | None = self._phase_repository.get_by_id(phase_id)
        if phase is None:
            raise ValueError("Phase not found")

        phase_status: PhaseStatus = self._status_calculator.calculate_phase_status(
            timeframe_start=phase.timeframe_start.date() if phase.timeframe_start else None,
            timeframe_end=phase.timeframe_end.date() if phase.timeframe_end else None,
            as_of_date=as_of.date(),
        )

        all_workouts: list[Workout] = self._workout_repository.list_by_phase_id(phase_id=phase_id)

        counts: dict[WorkoutStatus, int] = self._count_workouts_by_status(all_workouts)

        open_workouts: list[WorkoutContentResponse] = self._build_open_workout_content_responses(
            all_workouts=all_workouts
        )
        done_workouts: list[WorkoutDetailResponse] = self._build_done_workout_detail_responses(
            all_workouts=all_workouts
        )

        weekly_workouts: dict[datetime, list[Workout]] = defaultdict(list)
        for workout in all_workouts:
            if workout.planned_week_start_date is not None:
                weekly_workouts[workout.planned_week_start_date].append(workout)

        weekly_metrics: list[TrainingMetricsResponse]
        if weekly_workouts:
            weekly_metrics = [
                self._build_training_metrics_response(
                    workouts=workouts,
                    timeframe_start=week_start,
                    timeframe_end=get_week_end_for_date(week_start),
                )
                for week_start, workouts in sorted(weekly_workouts.items())
            ]
        elif all_workouts:
            weekly_metrics = [
                self._build_training_metrics_response(
                    workouts=all_workouts,
                    timeframe_start=phase.timeframe_start,
                    timeframe_end=phase.timeframe_end,
                )
            ]
        else:
            weekly_metrics = []

        data_gaps: list[str] = []

        if phase_status == PhaseStatus.UNKNOWN:
            data_gaps.append(
                "Phase timeframe is not fully defined; unable to determine phase status."
            )

        if self._can_check_unlinked_sessions(phase=phase, phase_status=phase_status):
            unlinked_sessions: list[SessionResponse] = [
                SessionResponse.model_validate(session)
                for session in self._session_repository.list_unlinked_within_window(
                    start=cast(datetime, phase.timeframe_start),
                    end=cast(datetime, phase.timeframe_end),
                )
            ]
            if unlinked_sessions:
                data_gaps.append(
                    self._count_message(
                        len(unlinked_sessions),
                        singular="session within the phase timeframe is not linked to any workout.",
                        plural=(
                            "sessions within the phase timeframe are not linked to any workouts."
                        ),
                    )
                )

        if counts[WorkoutStatus.UNKNOWN] > 0:
            data_gaps.append(
                self._count_message(
                    count=counts[WorkoutStatus.UNKNOWN],
                    singular="workout in this phase has an unknown status.",
                    plural="workouts in this phase have unknown statuses.",
                )
            )
        if counts[WorkoutStatus.MISSED] > 0:
            data_gaps.append(
                self._count_message(
                    count=counts[WorkoutStatus.MISSED],
                    singular="workout in this phase was missed.",
                    plural="workouts in this phase were missed.",
                )
            )

        metadata = ContextMetadataResponse(
            as_of_date=as_of.date(), timezone=as_of.tzname() or "UTC"
        )
        plan_summary: PlanSummaryResponse | None = PlanSummaryResponse.model_validate(phase.plan)
        phase_response: PhaseResponse = PhaseResponse.model_validate(phase)
        adherence = WorkoutAdherenceSummaryResponse(
            planned_workouts=len(all_workouts),
            completed_workouts=counts[WorkoutStatus.DONE],
            skipped_workouts=counts[WorkoutStatus.SKIPPED],
            unknown_workouts=counts[WorkoutStatus.UNKNOWN],
            completion_ratio=(counts[WorkoutStatus.DONE] / len(all_workouts))
            if all_workouts
            else None,
        )

        return PhaseContextResponse(
            metadata=metadata,
            plan_summary=plan_summary,
            phase_status=phase_status,
            phase=phase_response,
            open_workouts=open_workouts,
            done_workouts=done_workouts,
            weekly_metrics=weekly_metrics,
            adherence=adherence,
            data_gaps=data_gaps,
        )

    def get_specific_phase_week_context(
        self, phase_id: int, week_start_date: datetime
    ) -> PhaseWeekContextResponse:
        """Build and return the context snapshot for a specific training phase week.

        Args:
            phase_id: Primary key of the phase to build context for.
            week_start_date: The start date of the week within the phase to build context for.

        Returns:
            A ``PhaseContextResponse`` focused on the specified week.

        Raises:
            ValueError: If no phase with the given ``phase_id`` exists,
                or if the week number is invalid.
        """
        as_of = datetime.now(tz=UTC)

        phase: Phase | None = self._phase_repository.get_by_id(phase_id)
        if phase is None:
            raise ValueError("Phase not found")

        phase_status: PhaseStatus = self._status_calculator.calculate_phase_status(
            timeframe_start=phase.timeframe_start,
            timeframe_end=phase.timeframe_end,
            as_of_date=as_of.date(),
        )

        all_workouts: list[Workout] = self._workout_repository.list_within_planned_week(
            phase_id=phase_id, week_start_date=week_start_date
        )

        counts: dict[WorkoutStatus, int] = self._count_workouts_by_status(all_workouts)

        metrics: TrainingMetricsResponse = self._build_training_metrics_response(
            workouts=all_workouts,
            timeframe_start=week_start_date,
            timeframe_end=get_week_end_for_date(week_start_date),
        )

        data_gaps: list[str] = []

        if phase_status == PhaseStatus.UNKNOWN:
            data_gaps.append(
                "Phase timeframe is not fully defined; unable to determine phase status."
            )

        if self._can_check_unlinked_sessions(phase=phase, phase_status=phase_status):
            unlinked_sessions: list[SessionResponse] = [
                SessionResponse.model_validate(session)
                for session in self._session_repository.list_unlinked_within_window(
                    start=cast(datetime, phase.timeframe_start),
                    end=cast(datetime, phase.timeframe_end),
                )
            ]
            if unlinked_sessions:
                data_gaps.append(
                    self._count_message(
                        len(unlinked_sessions),
                        singular=(
                            "session within the phase timeframe is not linked to any workout."
                        ),
                        plural=(
                            "sessions within the phase timeframe are not linked to any workouts."
                        ),
                    )
                )

        if counts[WorkoutStatus.UNKNOWN] > 0:
            data_gaps.append(
                self._count_message(
                    count=counts[WorkoutStatus.UNKNOWN],
                    singular="workout in this phase week has an unknown status.",
                    plural="workouts in this phase week have unknown statuses.",
                )
            )
        if counts[WorkoutStatus.MISSED] > 0:
            data_gaps.append(
                self._count_message(
                    count=counts[WorkoutStatus.MISSED],
                    singular="workout in this phase week was missed.",
                    plural="workouts in this phase week were missed.",
                )
            )

        metadata = PhaseWeekContextMetadataResponse(
            as_of_date=as_of.date(),
            timezone=as_of.tzname() or "UTC",
            phase_week_number=get_phase_week_number_for_date(
                phase_start_date=phase.timeframe_start, date=week_start_date
            )
            if phase.timeframe_start
            else 0,
            phase_week_start_date=week_start_date,
            phase_week_end_date=get_week_end_for_date(week_start_date),
        )
        plan_summary: PlanSummaryResponse | None = PlanSummaryResponse.model_validate(phase.plan)
        phase_summary: PhaseSummaryResponse = PhaseSummaryResponse.model_validate(phase)
        adherence = WorkoutAdherenceSummaryResponse(
            planned_workouts=len(all_workouts),
            completed_workouts=counts[WorkoutStatus.DONE],
            skipped_workouts=counts[WorkoutStatus.SKIPPED],
            unknown_workouts=counts[WorkoutStatus.UNKNOWN],
            completion_ratio=(counts[WorkoutStatus.DONE] / len(all_workouts))
            if all_workouts
            else None,
        )

        return PhaseWeekContextResponse(
            metadata=metadata,
            plan_summary=plan_summary,
            phase_status=phase_status,
            phase_summary=phase_summary,
            workouts=[WorkoutDetailResponse.model_validate(workout) for workout in all_workouts],
            metrics=metrics,
            adherence=adherence,
            data_gaps=data_gaps,
        )
