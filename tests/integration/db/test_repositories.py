"""Integration tests for direct repository query methods."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.training import Plan
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.training_base_repository import TrainingBaseRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus
from tests.factories.training_models import (
    make_phase,
    make_plan,
    make_tracked_session,
    make_workout,
)

pytestmark = pytest.mark.integration


def test_training_base_repository_get_by_id_returns_none_for_missing_entity(
    db_session: Session,
) -> None:
    repo = TrainingBaseRepository[Plan](db_session, Plan)

    assert repo.get_by_id(999_999) is None


def test_workout_repository_list_by_phase_id_can_filter_by_status(db_session: Session) -> None:
    plan = make_plan(db_session, name="Repo Plan")
    phase = make_phase(db_session, plan=plan, name="Repo Phase")
    make_workout(db_session, phase=phase, name="done", status=WorkoutStatus.DONE)
    make_workout(db_session, phase=phase, name="open", status=WorkoutStatus.OPEN)

    workouts = WorkoutRepository(db_session).list_by_phase_id(
        phase.id,
        status=WorkoutStatus.DONE,
    )

    assert len(workouts) == 1
    assert workouts[0].name == "done"


def test_session_repository_list_by_workout_ids_returns_all_for_multiple_workouts(
    db_session: Session,
) -> None:
    plan = make_plan(db_session, name="Session Repo Plan")
    phase = make_phase(db_session, plan=plan, name="Session Repo Phase")
    workout_one = make_workout(db_session, phase=phase, name="w1")
    workout_two = make_workout(db_session, phase=phase, name="w2")

    make_tracked_session(
        db_session,
        workout=workout_one,
        name="s1",
        start=datetime.now(tz=UTC) - timedelta(hours=1),
    )
    make_tracked_session(
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
    plan = make_plan(db_session, name="Recent Plan")
    phase = make_phase(db_session, plan=plan, name="Recent Phase")
    workout = make_workout(db_session, phase=phase, name="Recent Workout")

    recent_start = datetime.now(tz=UTC) - timedelta(days=2)
    old_start = datetime.now(tz=UTC) - timedelta(days=20)

    recent = make_tracked_session(db_session, workout=workout, name="recent", start=recent_start)
    make_tracked_session(db_session, workout=workout, name="old", start=old_start)

    sessions = SessionRepository(db_session).list_recent(days=7)

    assert [session.id for session in sessions] == [recent.id]


def test_phase_repository_get_latest_by_plan_id_uses_most_recent_start(
    db_session: Session,
) -> None:
    plan = make_plan(db_session, name="Phase Repo Plan")
    earlier = make_phase(
        db_session,
        plan=plan,
        name="Earlier",
        timeframe_start=datetime(2026, 1, 1, tzinfo=UTC),
    )
    later = make_phase(
        db_session,
        plan=plan,
        name="Later",
        timeframe_start=datetime(2026, 2, 1, tzinfo=UTC),
    )

    latest = PhaseRepository(db_session).get_latest_by_plan_id(plan.id)

    assert latest is not None
    assert latest.id == later.id
    assert latest.id != earlier.id
