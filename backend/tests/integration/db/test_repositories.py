"""Integration tests for direct repository query methods."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.training import Plan
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.plan_repository import PlanRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.training_base_repository import TrainingBaseRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus
from ldk_athlete_ai_coach.utils.date_utils import get_week_start_for_date
from tests.factories.persisted_training_models import (
    create_phase,
    create_plan,
    create_tracked_session,
    create_workout,
)

pytestmark = pytest.mark.integration


def test_training_base_repository_get_by_id_returns_none_for_missing_entity(
    db_session: Session,
) -> None:
    repo = TrainingBaseRepository[Plan](db_session, Plan)

    assert repo.get_by_id(999_999) is None


def test_workout_repository_list_by_phase_id_can_filter_by_status(db_session: Session) -> None:
    plan = create_plan(db_session, name="Repo Plan")
    phase = create_phase(db_session, plan=plan, name="Repo Phase")
    create_workout(db_session, phase=phase, name="done", status=WorkoutStatus.DONE)
    create_workout(db_session, phase=phase, name="open", status=WorkoutStatus.OPEN)

    workouts = WorkoutRepository(db_session).list_by_phase_id(
        phase.id,
        status=WorkoutStatus.DONE,
    )

    assert len(workouts) == 1
    assert workouts[0].name == "done"


def test_session_repository_list_by_workout_ids_returns_all_for_multiple_workouts(
    db_session: Session,
) -> None:
    plan = create_plan(db_session, name="Session Repo Plan")
    phase = create_phase(db_session, plan=plan, name="Session Repo Phase")
    workout_one = create_workout(db_session, phase=phase, name="w1")
    workout_two = create_workout(db_session, phase=phase, name="w2")

    create_tracked_session(
        db_session,
        workout=workout_one,
        name="s1",
        start=datetime.now(tz=UTC) - timedelta(hours=1),
    )
    create_tracked_session(
        db_session,
        workout=workout_two,
        name="s2",
        start=datetime.now(tz=UTC),
    )

    sessions = SessionRepository(db_session).list_by_workout_ids([workout_one.id, workout_two.id])

    assert len(sessions) == 2
    assert {session.workout_id for session in sessions} == {workout_one.id, workout_two.id}


def test_session_repository_list_by_workout_ids_returns_empty_for_empty_input(
    db_session: Session,
) -> None:
    sessions = SessionRepository(db_session).list_by_workout_ids([])

    assert sessions == []


def test_session_repository_list_recent_respects_cutoff_days(db_session: Session) -> None:
    plan = create_plan(db_session, name="Recent Plan")
    phase = create_phase(db_session, plan=plan, name="Recent Phase")
    workout = create_workout(db_session, phase=phase, name="Recent Workout")

    recent_start = datetime.now(tz=UTC) - timedelta(days=2)
    old_start = datetime.now(tz=UTC) - timedelta(days=20)

    recent = create_tracked_session(
        db_session,
        workout=workout,
        name="recent",
        start=recent_start,
    )
    create_tracked_session(db_session, workout=workout, name="old", start=old_start)

    sessions = SessionRepository(db_session).list_recent(days=7)

    assert [session.id for session in sessions] == [recent.id]


def test_phase_repository_get_latest_by_plan_id_uses_most_recent_start(
    db_session: Session,
) -> None:
    plan = create_plan(db_session, name="Phase Repo Plan")
    earlier = create_phase(
        db_session,
        plan=plan,
        name="Earlier",
        timeframe_start=datetime(2026, 1, 1, tzinfo=UTC),
    )
    later = create_phase(
        db_session,
        plan=plan,
        name="Later",
        timeframe_start=datetime(2026, 2, 1, tzinfo=UTC),
    )

    latest = PhaseRepository(db_session).get_latest_by_plan_id(plan.id)

    assert latest is not None
    assert latest.id == later.id
    assert latest.id != earlier.id


def test_plan_repository_get_active_for_datetime_returns_latest_active_plan(
    db_session: Session,
) -> None:
    now = datetime(2026, 4, 20, 9, 0, tzinfo=UTC)
    create_plan(
        db_session,
        name="Past Plan",
        start_date_start=datetime(2026, 1, 1, tzinfo=UTC),
        end_date_start=datetime(2026, 2, 1, tzinfo=UTC),
    )
    earlier_active = create_plan(
        db_session,
        name="Earlier Active Plan",
        start_date_start=datetime(2026, 3, 1, tzinfo=UTC),
        end_date_start=datetime(2026, 4, 30, tzinfo=UTC),
    )
    later_active = create_plan(
        db_session,
        name="Later Active Plan",
        start_date_start=datetime(2026, 4, 1, tzinfo=UTC),
        end_date_start=datetime(2026, 5, 15, tzinfo=UTC),
    )

    active = PlanRepository(db_session).get_active_for_datetime(now)

    assert active is not None
    assert active.id == later_active.id
    assert active.id != earlier_active.id


def test_plan_repository_get_latest_falls_back_to_primary_key_order_when_dates_missing(
    db_session: Session,
) -> None:
    first = create_plan(db_session, name="Undated Plan A")
    second = create_plan(db_session, name="Undated Plan B")

    latest = PlanRepository(db_session).get_latest()

    assert latest is not None
    assert latest.id == second.id
    assert latest.id != first.id


def test_phase_repository_get_active_returns_latest_active_phase(
    db_session: Session,
) -> None:
    now = datetime(2026, 4, 20, 9, 0, tzinfo=UTC)
    plan = create_plan(
        db_session,
        name="Active Phase Plan",
        start_date_start=datetime(2026, 4, 1, tzinfo=UTC),
        end_date_start=datetime(2026, 5, 1, tzinfo=UTC),
    )
    create_phase(
        db_session,
        plan=plan,
        name="Past Phase",
        timeframe_start=datetime(2026, 3, 1, tzinfo=UTC),
        timeframe_end=datetime(2026, 3, 31, tzinfo=UTC),
    )
    earlier_active = create_phase(
        db_session,
        plan=plan,
        name="Earlier Active Phase",
        timeframe_start=datetime(2026, 4, 1, tzinfo=UTC),
        timeframe_end=datetime(2026, 4, 30, tzinfo=UTC),
    )
    later_active = create_phase(
        db_session,
        plan=plan,
        name="Later Active Phase",
        timeframe_start=datetime(2026, 4, 10, tzinfo=UTC),
        timeframe_end=datetime(2026, 4, 25, tzinfo=UTC),
    )

    active = PhaseRepository(db_session).get_active_for_datetime(now)

    assert active is not None
    assert active.id == later_active.id
    assert active.id != earlier_active.id


def test_phase_repository_get_by_date_returns_latest_matching_phase(db_session: Session) -> None:
    target = datetime(2026, 4, 20, 9, 0, tzinfo=UTC)
    create_phase(
        db_session,
        name="Non Matching Phase",
        plan=None,
        timeframe_start=datetime(2026, 5, 1, tzinfo=UTC),
        timeframe_end=datetime(2026, 5, 31, tzinfo=UTC),
    )
    earlier = create_phase(
        db_session,
        name="Earlier Matching Phase",
        plan=None,
        timeframe_start=datetime(2026, 4, 1, tzinfo=UTC),
        timeframe_end=datetime(2026, 4, 30, tzinfo=UTC),
    )
    later = create_phase(
        db_session,
        name="Later Matching Phase",
        plan=None,
        timeframe_start=datetime(2026, 4, 10, tzinfo=UTC),
        timeframe_end=datetime(2026, 4, 25, tzinfo=UTC),
    )

    result = PhaseRepository(db_session).get_by_date(target)

    assert result is not None
    assert result.id == later.id
    assert result.id != earlier.id


def test_phase_repository_list_by_timeframe_window_returns_overlapping_phases_in_order(
    db_session: Session,
) -> None:
    first = create_phase(
        db_session,
        plan=None,
        name="First Overlap",
        timeframe_start=datetime(2026, 4, 1, tzinfo=UTC),
        timeframe_end=datetime(2026, 4, 10, tzinfo=UTC),
    )
    second = create_phase(
        db_session,
        plan=None,
        name="Second Overlap",
        timeframe_start=datetime(2026, 4, 5, tzinfo=UTC),
        timeframe_end=datetime(2026, 4, 15, tzinfo=UTC),
    )
    create_phase(
        db_session,
        plan=None,
        name="Outside Window",
        timeframe_start=datetime(2026, 5, 1, tzinfo=UTC),
        timeframe_end=datetime(2026, 5, 10, tzinfo=UTC),
    )

    phases = PhaseRepository(db_session).list_by_timeframe_window(
        start=datetime(2026, 4, 8, tzinfo=UTC),
        end=datetime(2026, 4, 12, tzinfo=UTC),
    )

    assert [phase.id for phase in phases] == [first.id, second.id]


def test_workout_repository_list_upcoming_by_phase_id_filters_and_orders_results(
    db_session: Session,
) -> None:
    now = datetime(2026, 4, 25, 9, 0, tzinfo=UTC)
    plan = create_plan(db_session, name="Upcoming Plan")
    phase = create_phase(db_session, plan=plan, name="Upcoming Phase")
    current_week_start = get_week_start_for_date(now)
    first = create_workout(
        db_session,
        phase=phase,
        name="Soon",
        date_start=now + timedelta(hours=1),
        planned_week_start_date=current_week_start,
        status="Open",
    )
    second = create_workout(
        db_session,
        phase=phase,
        name="Later",
        date_start=now + timedelta(days=1),
        planned_week_start_date=current_week_start,
        status="Open",
    )
    create_workout(
        db_session,
        phase=phase,
        name="Past Effective Date",
        date_start=now - timedelta(days=1),
        planned_week_start_date=current_week_start,
        status="Done",
    )
    create_workout(
        db_session,
        phase=phase,
        name="Old Planned Week",
        date_start=now + timedelta(days=2),
        planned_week_start_date=current_week_start - timedelta(days=7),
        status="Open",
    )

    workouts = WorkoutRepository(db_session).list_upcoming_by_phase_id(phase.id, now)

    assert [workout.id for workout in workouts] == [first.id, second.id]


def test_workout_repository_list_within_effective_date_window_respects_phase_filters(
    db_session: Session,
) -> None:
    window_start = datetime(2026, 4, 10, tzinfo=UTC)
    window_end = datetime(2026, 4, 20, tzinfo=UTC)
    phase = create_phase(db_session, plan=None, name="Window Phase")
    with_phase = create_workout(
        db_session,
        phase=phase,
        name="With Phase",
        date_start=datetime(2026, 4, 12, tzinfo=UTC),
        status="Open",
    )
    with_effective_done_date = create_workout(
        db_session,
        phase=phase,
        name="Done Date Match",
        date_start=None,
        done_date_start=datetime(2026, 4, 18, tzinfo=UTC),
        status="Done",
    )
    without_phase = create_workout(
        db_session,
        phase=None,
        name="Without Phase",
        date_start=datetime(2026, 4, 15, tzinfo=UTC),
        status="Open",
    )
    create_workout(
        db_session,
        phase=phase,
        name="Outside Window",
        date_start=datetime(2026, 4, 25, tzinfo=UTC),
        status="Open",
    )
    repo = WorkoutRepository(db_session)

    all_workouts = repo.list_within_effective_date_window(window_start, window_end)
    with_phase_only = repo.list_within_effective_date_window(
        window_start,
        window_end,
        phase_filter="with_phase",
    )
    without_phase_only = repo.list_within_effective_date_window(
        window_start,
        window_end,
        phase_filter="without_phase",
    )

    assert [workout.id for workout in all_workouts] == [
        with_effective_done_date.id,
        without_phase.id,
        with_phase.id,
    ]
    assert [workout.id for workout in with_phase_only] == [
        with_effective_done_date.id,
        with_phase.id,
    ]
    assert [workout.id for workout in without_phase_only] == [without_phase.id]


def test_workout_repository_list_within_planned_week_returns_matching_workouts(
    db_session: Session,
) -> None:
    phase = create_phase(db_session, plan=None, name="Week Filter Phase")
    week_start = datetime(2026, 4, 14, tzinfo=UTC)
    matching = create_workout(
        db_session,
        phase=phase,
        name="Matching Week Workout",
        planned_week_start_date=week_start,
        status="Open",
    )
    create_workout(
        db_session,
        phase=phase,
        name="Other Week Workout",
        planned_week_start_date=week_start + timedelta(days=7),
        status="Open",
    )

    workouts = WorkoutRepository(db_session).list_within_planned_week(phase.id, week_start)

    assert [workout.id for workout in workouts] == [matching.id]


def test_workout_repository_count_unscheduled_by_phase_id_counts_only_unscheduled_workouts(
    db_session: Session,
) -> None:
    phase = create_phase(db_session, plan=None, name="Unscheduled Phase")
    other_phase = create_phase(db_session, plan=None, name="Other Phase")
    create_workout(db_session, phase=phase, name="Unscheduled A", date_start=None, status="Open")
    create_workout(
        db_session,
        phase=phase,
        name="Scheduled B",
        date_start=datetime(2026, 4, 15, tzinfo=UTC),
        status="Open",
    )
    create_workout(
        db_session,
        phase=other_phase,
        name="Other Phase Unscheduled",
        date_start=None,
        status="Open",
    )

    count = WorkoutRepository(db_session).count_unscheduled_by_phase_id(phase.id)

    assert count == 1
