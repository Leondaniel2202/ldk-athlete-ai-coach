"""Tests for the phase-context application service."""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ldk_athlete_ai_coach.application.services.phase_context_service import PhaseContextService
from ldk_athlete_ai_coach.db.base import Base
from ldk_athlete_ai_coach.db.models.training import Phase, Plan, TrackedSession, Workout
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository

pytestmark = pytest.mark.integration

_SQLITE_URL = "sqlite:///:memory:"

_engine = create_engine(
    _SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSessionLocal = sessionmaker(bind=_engine, class_=Session)


@pytest.fixture(autouse=True)
def _create_tables() -> Generator[None, None, None]:
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=_engine)
    yield  # type: ignore[misc]
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Return a fresh test database session."""
    session = _TestingSessionLocal()
    yield session  # type: ignore[misc]
    session.close()


def _make_plan(
    db: Session,
    name: str,
    *,
    start_date_start: datetime | None = None,
    end_date_start: datetime | None = None,
) -> Plan:
    plan = Plan(
        notion_page_id=f"plan-{name}",
        notion_url=f"https://notion.so/plan-{name}",
        name=name,
        start_date_start=start_date_start,
        end_date_start=end_date_start,
        start_date_is_datetime=False,
        end_date_is_datetime=False,
    )
    db.add(plan)
    db.flush()
    return plan


def _make_phase(
    db: Session,
    plan: Plan,
    name: str,
    *,
    timeframe_start: datetime | None = None,
    timeframe_end: datetime | None = None,
) -> Phase:
    phase = Phase(
        notion_page_id=f"phase-{name}",
        notion_url=f"https://notion.so/phase-{name}",
        name=name,
        focus_tags=[],
        timeframe_start=timeframe_start,
        timeframe_end=timeframe_end,
        timeframe_is_datetime=False,
        plan_id=plan.id,
    )
    db.add(phase)
    db.flush()
    return phase


def _make_workout(
    db: Session,
    phase: Phase,
    name: str,
    *,
    date_start: datetime | None = None,
    done_date_start: datetime | None = None,
    status: str | None = "Done",
    skipped: bool = False,
) -> Workout:
    workout = Workout(
        notion_page_id=f"workout-{name}",
        notion_url=f"https://notion.so/workout-{name}",
        name=name,
        notion_page_content=f"Instructions for {name}",
        equipment=[],
        metrics_to_record=[],
        purpose=[],
        primarily_used_muscle_group=[],
        date_start=date_start,
        date_is_datetime=date_start is not None,
        done_date_start=done_date_start,
        done_date_is_datetime=done_date_start is not None,
        status=status,
        cancelled=False,
        skipped=skipped,
        phase_id=phase.id,
    )
    db.add(workout)
    db.flush()
    return workout


def _make_session(
    db: Session,
    workout: Workout | None,
    *,
    name: str,
    start_start: datetime,
) -> TrackedSession:
    tracked_session = TrackedSession(
        notion_page_id=f"session-{name}",
        notion_url=f"https://notion.so/session-{name}",
        name=name,
        start_is_datetime=True,
        end_is_datetime=False,
        start_start=start_start,
        workout_id=workout.id if workout is not None else None,
    )
    db.add(tracked_session)
    db.flush()
    return tracked_session


def _make_service(db: Session) -> PhaseContextService:
    return PhaseContextService(
        phase_repository=PhaseRepository(db),
        workout_repository=WorkoutRepository(db),
        session_repository=SessionRepository(db),
    )


def test_service_returns_specific_phase_context_with_grouped_workouts(
    db_session: Session,
) -> None:
    """The service returns the requested phase with open and done workouts grouped."""
    now = datetime.now(tz=UTC)
    plan = _make_plan(
        db_session,
        name="Build Plan",
        start_date_start=now - timedelta(days=14),
        end_date_start=now + timedelta(days=14),
    )
    phase = _make_phase(
        db_session,
        plan,
        name="Specific Build",
        timeframe_start=now - timedelta(days=7),
        timeframe_end=now + timedelta(days=7),
    )
    open_workout = _make_workout(
        db_session,
        phase,
        name="Open Workout",
        date_start=now + timedelta(days=1),
        status="Open",
    )
    done_workout = _make_workout(
        db_session,
        phase,
        name="Done Workout",
        date_start=now - timedelta(days=2),
        done_date_start=now - timedelta(days=1),
        status="Done",
    )
    _make_session(
        db_session,
        done_workout,
        name="Completed Session",
        start_start=now - timedelta(hours=12),
    )

    context = _make_service(db_session).get_specific_phase_context(phase.id)

    assert context.plan_summary.id == plan.id
    assert context.phase.id == phase.id
    assert [workout.id for workout in context.open_workouts] == [open_workout.id]
    assert [workout.id for workout in context.done_workouts] == [done_workout.id]
    assert context.done_workouts[0].tracked_sessions[0].name == "Completed Session"
    assert context.adherence.planned_workouts == 2
    assert context.adherence.completed_workouts == 1
    assert context.adherence.skipped_workouts == 0
    assert context.adherence.unknown_workouts == 0
    assert context.data_gaps == []


def test_service_reports_unlinked_sessions_and_status_data_gaps(
    db_session: Session,
) -> None:
    """The service surfaces unlinked sessions and problematic workout statuses."""
    now = datetime.now(tz=UTC)
    plan = _make_plan(
        db_session,
        name="Gap Plan",
        start_date_start=now - timedelta(days=14),
        end_date_start=now + timedelta(days=14),
    )
    phase = _make_phase(
        db_session,
        plan,
        name="Gap Phase",
        timeframe_start=now - timedelta(days=7),
        timeframe_end=now + timedelta(days=7),
    )
    _make_workout(
        db_session,
        phase,
        name="Unknown Workout",
        date_start=now - timedelta(days=2),
        status="Unknown",
    )
    _make_workout(
        db_session,
        phase,
        name="Missed Workout",
        date_start=now - timedelta(days=1),
        status="Missed",
    )
    _make_session(
        db_session,
        None,
        name="Unlinked Session",
        start_start=now,
    )

    context = _make_service(db_session).get_specific_phase_context(phase.id)

    assert "1 session within the phase timeframe is not linked to any workout." in context.data_gaps
    assert "1 workout in this phase has an unknown status." in context.data_gaps
    assert "1 workout in this phase was missed." in context.data_gaps


def test_service_raises_for_missing_phase(db_session: Session) -> None:
    """The service raises a clear error when the phase does not exist."""
    with pytest.raises(ValueError, match="Phase not found"):
        _make_service(db_session).get_specific_phase_context(phase_id=999)
