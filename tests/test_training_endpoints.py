"""Tests for V1 training domain endpoints (plans, phases, workouts, sessions)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ldk_athlete_ai_coach.db.base import Base
from ldk_athlete_ai_coach.db.models.training import Phase, Plan, TrackedSession, Workout
from ldk_athlete_ai_coach.db.session import get_db_session
from ldk_athlete_ai_coach.main import app

# ---------------------------------------------------------------------------
# In-memory SQLite setup
# ---------------------------------------------------------------------------

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
    return _TestingSessionLocal()


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    """Return a test client wired to the in-memory database."""

    def _override() -> Session:
        return db_session

    app.dependency_overrides[get_db_session] = _override
    tc = TestClient(app)
    yield tc  # type: ignore[misc]
    app.dependency_overrides.clear()
    db_session.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_plan(db: Session, name: str = "Base Plan") -> Plan:
    plan = Plan(
        notion_page_id=f"plan-{name}",
        notion_url=f"https://notion.so/plan-{name}",
        name=name,
        start_date_is_datetime=False,
        end_date_is_datetime=False,
    )
    db.add(plan)
    db.flush()
    return plan


def _make_phase(db: Session, name: str = "Base Phase", plan: Plan | None = None) -> Phase:
    phase = Phase(
        notion_page_id=f"phase-{name}",
        notion_url=f"https://notion.so/phase-{name}",
        name=name,
        focus_tags=[],
        timeframe_is_datetime=False,
        plan_id=plan.id if plan is not None else None,
    )
    db.add(phase)
    db.flush()
    return phase


def _make_workout(db: Session, phase: Phase, name: str = "Long Run") -> Workout:
    workout = Workout(
        notion_page_id=f"workout-{name}",
        notion_url=f"https://notion.so/workout-{name}",
        name=name,
        notion_page_content="Warm-up\nMain set\nCool-down",
        equipment=[],
        metrics_to_record=[],
        purpose=[],
        primarily_used_muscle_group=[],
        planned_training_load=360.0,
        actual_duration_min=58.0,
        actual_distance_km=10.2,
        actual_training_load=390.0,
        actual_calories_burned_kcal=720.0,
        weighted_hrr_intensity_sum=145.5,
        actual_hrr_intensity=2.51,
        status="Done",
        training_load_method="Weighted HRR",
        date_is_datetime=False,
        cancelled=False,
        skipped=False,
        phase_id=phase.id,
    )
    db.add(workout)
    db.flush()
    return workout


def _make_session(
    db: Session,
    workout: Workout | None = None,
    *,
    start: datetime | None = None,
    name: str = "Morning Run",
) -> TrackedSession:
    tracked = TrackedSession(
        notion_page_id=f"session-{name}",
        notion_url=f"https://notion.so/session-{name}",
        name=name,
        start_is_datetime=True,
        end_is_datetime=False,
        start_start=start or datetime.now(tz=UTC),
        workout_id=workout.id if workout else None,
    )
    db.add(tracked)
    db.flush()
    return tracked


# ---------------------------------------------------------------------------
# Phase endpoints
# ---------------------------------------------------------------------------


def test_get_plan_returns_plan(client: TestClient, db_session: Session) -> None:
    """GET /plans/{id} returns the plan for a known ID."""
    plan = _make_plan(db_session)

    response = client.get(f"/api/v1/plans/{plan.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == plan.id
    assert data["name"] == plan.name


def test_get_plan_returns_404_for_missing_plan(client: TestClient) -> None:
    """GET /plans/{id} returns 404 when the plan does not exist."""
    response = client.get("/api/v1/plans/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Plan not found"


def test_get_plan_phases_returns_list(client: TestClient, db_session: Session) -> None:
    """GET /plans/{id}/phases returns all phases for the plan."""
    plan = _make_plan(db_session)
    p1 = _make_phase(db_session, name="Phase A", plan=plan)
    p2 = _make_phase(db_session, name="Phase B", plan=plan)

    response = client.get(f"/api/v1/plans/{plan.id}/phases")

    assert response.status_code == 200
    ids = {phase["id"] for phase in response.json()}
    assert ids == {p1.id, p2.id}


def test_get_plan_phases_returns_empty_list_when_no_phases(
    client: TestClient, db_session: Session
) -> None:
    """GET /plans/{id}/phases returns [] when plan has no phases."""
    plan = _make_plan(db_session)

    response = client.get(f"/api/v1/plans/{plan.id}/phases")

    assert response.status_code == 200
    assert response.json() == []


def test_get_plan_phases_returns_404_for_missing_plan(client: TestClient) -> None:
    """GET /plans/{id}/phases returns 404 when the plan does not exist."""
    response = client.get("/api/v1/plans/999/phases")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Phase endpoints
# ---------------------------------------------------------------------------


def test_get_phase_returns_phase(client: TestClient, db_session: Session) -> None:
    """GET /phases/{id} returns the phase for a known ID."""
    phase = _make_phase(db_session)

    response = client.get(f"/api/v1/phases/{phase.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == phase.id
    assert data["name"] == phase.name


def test_get_phase_returns_404_for_missing_phase(client: TestClient) -> None:
    """GET /phases/{id} returns 404 when the phase does not exist."""
    response = client.get("/api/v1/phases/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Phase not found"


def test_get_phase_workouts_returns_list(client: TestClient, db_session: Session) -> None:
    """GET /phases/{id}/workouts returns all workouts for the phase."""
    phase = _make_phase(db_session)
    w1 = _make_workout(db_session, phase, name="Run A")
    w2 = _make_workout(db_session, phase, name="Run B")

    response = client.get(f"/api/v1/phases/{phase.id}/workouts")

    assert response.status_code == 200
    ids = {w["id"] for w in response.json()}
    assert ids == {w1.id, w2.id}


def test_get_phase_workouts_returns_empty_list_when_no_workouts(
    client: TestClient, db_session: Session
) -> None:
    """GET /phases/{id}/workouts returns [] when phase has no workouts."""
    phase = _make_phase(db_session)

    response = client.get(f"/api/v1/phases/{phase.id}/workouts")

    assert response.status_code == 200
    assert response.json() == []


def test_get_phase_workouts_returns_404_for_missing_phase(client: TestClient) -> None:
    """GET /phases/{id}/workouts returns 404 when the phase does not exist."""
    response = client.get("/api/v1/phases/999/workouts")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Workout endpoints
# ---------------------------------------------------------------------------


def test_get_workout_returns_workout(client: TestClient, db_session: Session) -> None:
    """GET /workouts/{id} returns the workout for a known ID."""
    phase = _make_phase(db_session)
    workout = _make_workout(db_session, phase)

    response = client.get(f"/api/v1/workouts/{workout.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workout.id
    assert data["name"] == workout.name
    assert data["notion_page_content"] == "Warm-up\nMain set\nCool-down"
    assert data["planned_training_load"] == 360.0
    assert data["actual_duration_min"] == 58.0
    assert data["actual_distance_km"] == 10.2
    assert data["actual_training_load"] == 390.0
    assert data["actual_calories_burned_kcal"] == 720.0
    assert data["weighted_hrr_intensity_sum"] == 145.5
    assert data["actual_hrr_intensity"] == 2.51
    assert data["status"] == "Done"
    assert data["training_load_method"] == "Weighted HRR"


def test_get_workout_returns_404_for_missing_workout(client: TestClient) -> None:
    """GET /workouts/{id} returns 404 when the workout does not exist."""
    response = client.get("/api/v1/workouts/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout not found"


def test_get_workout_sessions_returns_list(client: TestClient, db_session: Session) -> None:
    """GET /workouts/{id}/sessions returns all sessions linked to the workout."""
    phase = _make_phase(db_session)
    workout = _make_workout(db_session, phase)
    s1 = _make_session(db_session, workout, name="Session A")
    s2 = _make_session(db_session, workout, name="Session B")

    response = client.get(f"/api/v1/workouts/{workout.id}/sessions")

    assert response.status_code == 200
    ids = {s["id"] for s in response.json()}
    assert ids == {s1.id, s2.id}


def test_get_workout_sessions_returns_404_for_missing_workout(client: TestClient) -> None:
    """GET /workouts/{id}/sessions returns 404 when the workout does not exist."""
    response = client.get("/api/v1/workouts/999/sessions")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Session endpoints
# ---------------------------------------------------------------------------


def test_get_session_returns_session(client: TestClient, db_session: Session) -> None:
    """GET /sessions/{id} returns the session for a known ID."""
    tracked = _make_session(db_session)

    response = client.get(f"/api/v1/sessions/{tracked.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tracked.id
    assert data["name"] == tracked.name


def test_get_session_returns_404_for_missing_session(client: TestClient) -> None:
    """GET /sessions/{id} returns 404 when the session does not exist."""
    response = client.get("/api/v1/sessions/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_get_recent_sessions_returns_sessions_within_window(
    client: TestClient, db_session: Session
) -> None:
    """GET /sessions/recent returns only sessions within the requested window."""
    now = datetime.now(tz=UTC)
    recent = _make_session(db_session, start=now - timedelta(days=3), name="Recent Session")
    _make_session(db_session, start=now - timedelta(days=30), name="Old Session")

    response = client.get("/api/v1/sessions/recent?days=14")

    assert response.status_code == 200
    ids = [s["id"] for s in response.json()]
    assert recent.id in ids
    assert all(s["id"] != _make_session.__name__ for s in response.json())
    # Old session must not appear
    for s in response.json():
        assert s["name"] != "Old Session"


def test_get_recent_sessions_default_window(client: TestClient, db_session: Session) -> None:
    """GET /sessions/recent uses a 14-day default when no days param is given."""
    now = datetime.now(tz=UTC)
    recent = _make_session(db_session, start=now - timedelta(days=7), name="Recent Default")

    response = client.get("/api/v1/sessions/recent")

    assert response.status_code == 200
    ids = [s["id"] for s in response.json()]
    assert recent.id in ids


def test_get_recent_sessions_rejects_invalid_days(client: TestClient) -> None:
    """GET /sessions/recent returns 422 when days < 1."""
    response = client.get("/api/v1/sessions/recent?days=0")

    assert response.status_code == 422
