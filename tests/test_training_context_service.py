"""Tests for the training-context domain service."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ldk_athlete_ai_coach.db.base import Base
from ldk_athlete_ai_coach.db.models.training import Phase, Plan, TrackedSession, Workout
from ldk_athlete_ai_coach.db.repositories.phase_repository import PhaseRepository
from ldk_athlete_ai_coach.db.repositories.plan_repository import PlanRepository
from ldk_athlete_ai_coach.db.repositories.session_repository import SessionRepository
from ldk_athlete_ai_coach.db.repositories.workout_repository import WorkoutRepository
from ldk_athlete_ai_coach.domain.training_context_service import TrainingContextService

_SQLITE_URL = "sqlite:///:memory:"

_engine = create_engine(
    _SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSessionLocal = sessionmaker(bind=_engine, class_=Session)


@pytest.fixture(autouse=True)
def _create_tables() -> None:
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=_engine)
    yield  # type: ignore[misc]
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture()
def db_session() -> Session:
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


def _make_service(db: Session) -> TrainingContextService:
    return TrainingContextService(
        plan_repository=PlanRepository(db),
        phase_repository=PhaseRepository(db),
        workout_repository=WorkoutRepository(db),
        session_repository=SessionRepository(db),
    )


def test_service_prefers_active_plan_and_phase_window(db_session: Session) -> None:
    """The service selects active window matches over later historical rows."""
    now = datetime(2026, 4, 12, 10, 0, tzinfo=UTC)
    _make_plan(
        db_session,
        name="Past Plan",
        start_date_start=now - timedelta(days=90),
        end_date_start=now - timedelta(days=60),
    )
    active_plan = _make_plan(
        db_session,
        name="Active Plan",
        start_date_start=now - timedelta(days=14),
        end_date_start=now + timedelta(days=14),
    )
    _make_phase(
        db_session,
        active_plan,
        name="Past Phase",
        timeframe_start=now - timedelta(days=21),
        timeframe_end=now - timedelta(days=8),
    )
    active_phase = _make_phase(
        db_session,
        active_plan,
        name="Active Phase",
        timeframe_start=now - timedelta(days=7),
        timeframe_end=now + timedelta(days=7),
    )

    context = _make_service(db_session).get_current_context(now)

    assert context.current.plan is not None
    assert context.current.phase is not None
    assert context.current.plan.id == active_plan.id
    assert context.current.phase.id == active_phase.id
    assert context.data_gaps == []


def test_service_falls_back_to_latest_plan_and_phase_when_no_active_match(db_session: Session) -> None:
    """The service uses the latest plan and phase when no active windows exist."""
    now = datetime(2026, 4, 12, 10, 0, tzinfo=UTC)
    _make_plan(
        db_session,
        name="Older Plan",
        start_date_start=now - timedelta(days=120),
        end_date_start=now - timedelta(days=90),
    )
    latest_plan = _make_plan(
        db_session,
        name="Latest Plan",
        start_date_start=now - timedelta(days=40),
        end_date_start=now - timedelta(days=10),
    )
    _make_phase(
        db_session,
        latest_plan,
        name="Older Phase",
        timeframe_start=now - timedelta(days=35),
        timeframe_end=now - timedelta(days=21),
    )
    latest_phase = _make_phase(
        db_session,
        latest_plan,
        name="Latest Phase",
        timeframe_start=now - timedelta(days=14),
        timeframe_end=now - timedelta(days=3),
    )

    context = _make_service(db_session).get_current_context(now)

    assert context.current.plan is not None
    assert context.current.phase is not None
    assert context.current.plan.id == latest_plan.id
    assert context.current.phase.id == latest_phase.id
    assert "No active plan matched the current date; using the latest available plan instead." in context.data_gaps
    assert "No active phase matched the current date; using the latest phase for the selected plan instead." in context.data_gaps


def test_service_computes_current_phase_week_from_phase_start(db_session: Session) -> None:
    """The service derives the current phase week from the phase start date."""
    now = datetime(2026, 4, 12, 10, 0, tzinfo=UTC)
    plan = _make_plan(
        db_session,
        name="Week Plan",
        start_date_start=now - timedelta(days=30),
        end_date_start=now + timedelta(days=30),
    )
    _make_phase(
        db_session,
        plan,
        name="Week Phase",
        timeframe_start=now - timedelta(days=15),
        timeframe_end=now + timedelta(days=10),
    )

    context = _make_service(db_session).get_current_context(now)

    assert context.current.current_phase_week == 3


def test_service_recent_workouts_use_effective_date(db_session: Session) -> None:
    """Recent workouts use done date first and planned date as fallback."""
    now = datetime(2026, 4, 12, 10, 0, tzinfo=UTC)
    plan = _make_plan(
        db_session,
        name="Recent Plan",
        start_date_start=now - timedelta(days=30),
        end_date_start=now + timedelta(days=30),
    )
    phase = _make_phase(
        db_session,
        plan,
        name="Recent Phase",
        timeframe_start=now - timedelta(days=10),
        timeframe_end=now + timedelta(days=10),
    )
    included_by_done_date = _make_workout(
        db_session,
        phase,
        name="Done Recently",
        date_start=now - timedelta(days=30),
        done_date_start=now - timedelta(days=2),
    )
    _make_workout(
        db_session,
        phase,
        name="Done Too Early",
        date_start=now - timedelta(days=2),
        done_date_start=now - timedelta(days=10),
    )
    included_by_planned_date = _make_workout(
        db_session,
        phase,
        name="Planned Recently",
        date_start=now - timedelta(days=3),
    )

    context = _make_service(db_session).get_current_context(now)

    assert [item.workout.id for item in context.recent_workouts] == [
        included_by_done_date.id,
        included_by_planned_date.id,
    ]


def test_service_aggregates_last_seven_days_adherence(db_session: Session) -> None:
    """The service summarizes planned, completed, and skipped workouts."""
    now = datetime(2026, 4, 12, 10, 0, tzinfo=UTC)
    plan = _make_plan(
        db_session,
        name="Adherence Plan",
        start_date_start=now - timedelta(days=30),
        end_date_start=now + timedelta(days=30),
    )
    phase = _make_phase(
        db_session,
        plan,
        name="Adherence Phase",
        timeframe_start=now - timedelta(days=10),
        timeframe_end=now + timedelta(days=10),
    )
    completed = _make_workout(
        db_session,
        phase,
        name="Completed",
        date_start=now - timedelta(days=1),
        done_date_start=now - timedelta(hours=12),
        status="Done",
    )
    _make_workout(
        db_session,
        phase,
        name="Skipped",
        date_start=now - timedelta(days=2),
        status="Skipped",
        skipped=True,
    )
    _make_workout(
        db_session,
        phase,
        name="Open",
        date_start=now - timedelta(days=3),
        status="Planned",
    )
    _make_workout(
        db_session,
        phase,
        name="Old",
        date_start=now - timedelta(days=10),
        status="Done",
    )
    _make_session(
        db_session,
        completed,
        name="Completed Session",
        start_start=now - timedelta(hours=10),
    )

    context = _make_service(db_session).get_current_context(now)

    assert context.adherence.planned_workouts == 3
    assert context.adherence.completed_workouts == 1
    assert context.adherence.skipped_workouts == 1
    assert context.adherence.completion_ratio == pytest.approx(1 / 3)
