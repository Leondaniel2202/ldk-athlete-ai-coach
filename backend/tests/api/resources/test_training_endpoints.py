"""Tests for V1 resource endpoints (plans, phases, workouts, sessions)."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.factories.persisted_training_models import (
    create_phase,
    create_plan,
    create_tracked_session,
    create_workout,
)

pytestmark = pytest.mark.api


def _iso_z(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def test_get_plan_returns_plan(client: TestClient, db_session: Session) -> None:
    """GET /plans/{id} returns the plan for a known ID."""
    plan = create_plan(db_session)

    response = client.get(f"/api/v1/resources/plans/{plan.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == plan.id
    assert data["name"] == plan.name


def test_get_plan_returns_404_for_missing_plan(client: TestClient) -> None:
    """GET /plans/{id} returns 404 when the plan does not exist."""
    response = client.get("/api/v1/resources/plans/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Plan not found"


def test_get_plan_summary_returns_summary(client: TestClient, db_session: Session) -> None:
    """GET /plans/{id}/summary returns the compact summary payload."""
    start = datetime(2026, 4, 1, tzinfo=UTC)
    plan = create_plan(db_session, name="Summary Plan", start_date_start=start)

    response = client.get(f"/api/v1/resources/plans/{plan.id}/summary")

    assert response.status_code == 200
    assert response.json() == {
        "id": plan.id,
        "name": "Summary Plan",
        "description": None,
        "start_date": date(2026, 4, 1).isoformat(),
        "end_date": date(2026, 12, 31).isoformat(),
    }


def test_get_plan_summary_returns_404_for_missing_plan(client: TestClient) -> None:
    """GET /plans/{id}/summary returns 404 when the plan does not exist."""
    response = client.get("/api/v1/resources/plans/999/summary")

    assert response.status_code == 404
    assert response.json()["detail"] == "Plan not found"


def test_get_plan_phases_returns_list(client: TestClient, db_session: Session) -> None:
    """GET /plans/{id}/phases returns all phases for the plan."""
    plan = create_plan(db_session)
    p1 = create_phase(db_session, name="Phase A", plan=plan)
    p2 = create_phase(db_session, name="Phase B", plan=plan)

    response = client.get(f"/api/v1/resources/plans/{plan.id}/phases")

    assert response.status_code == 200
    ids = {phase["id"] for phase in response.json()}
    assert ids == {p1.id, p2.id}


def test_get_plan_phases_returns_empty_list_when_no_phases(
    client: TestClient, db_session: Session
) -> None:
    """GET /plans/{id}/phases returns [] when plan has no phases."""
    plan = create_plan(db_session)

    response = client.get(f"/api/v1/resources/plans/{plan.id}/phases")

    assert response.status_code == 200
    assert response.json() == []


def test_get_plan_phases_returns_404_for_missing_plan(client: TestClient) -> None:
    """GET /plans/{id}/phases returns 404 when the plan does not exist."""
    response = client.get("/api/v1/resources/plans/999/phases")

    assert response.status_code == 404


def test_get_phase_returns_phase(client: TestClient, db_session: Session) -> None:
    """GET /phases/{id} returns the phase for a known ID."""
    phase = create_phase(db_session)

    response = client.get(f"/api/v1/resources/phases/{phase.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == phase.id
    assert data["name"] == phase.name


def test_get_phase_returns_404_for_missing_phase(client: TestClient) -> None:
    """GET /phases/{id} returns 404 when the phase does not exist."""
    response = client.get("/api/v1/resources/phases/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Phase not found"


def test_get_phase_summary_returns_summary(client: TestClient, db_session: Session) -> None:
    """GET /phases/{id}/summary returns the compact summary payload."""
    start = datetime(2026, 4, 7, tzinfo=UTC)
    end = datetime(2026, 4, 20, tzinfo=UTC)
    phase = create_phase(
        db_session,
        name="Summary Phase",
        timeframe_start=start,
        timeframe_end=end,
    )

    response = client.get(f"/api/v1/resources/phases/{phase.id}/summary")

    assert response.status_code == 200
    assert response.json() == {
        "id": phase.id,
        "name": "Summary Phase",
        "phase_type": "Base",
        "start_date": date(2026, 4, 7).isoformat(),
        "end_date": date(2026, 4, 20).isoformat(),
    }


def test_get_phase_summary_returns_404_for_missing_phase(client: TestClient) -> None:
    """GET /phases/{id}/summary returns 404 when the phase does not exist."""
    response = client.get("/api/v1/resources/phases/999/summary")

    assert response.status_code == 404
    assert response.json()["detail"] == "Phase not found"


def test_get_phase_workouts_returns_list(client: TestClient, db_session: Session) -> None:
    """GET /phases/{id}/workouts returns all workouts for the phase."""
    phase = create_phase(db_session)
    w1 = create_workout(db_session, phase, name="Run A")
    w2 = create_workout(db_session, phase, name="Run B")

    response = client.get(f"/api/v1/resources/phases/{phase.id}/workouts")

    assert response.status_code == 200
    ids = {workout["id"] for workout in response.json()}
    assert ids == {w1.id, w2.id}


def test_get_phase_workouts_returns_empty_list_when_no_workouts(
    client: TestClient, db_session: Session
) -> None:
    """GET /phases/{id}/workouts returns [] when phase has no workouts."""
    phase = create_phase(db_session)

    response = client.get(f"/api/v1/resources/phases/{phase.id}/workouts")

    assert response.status_code == 200
    assert response.json() == []


def test_get_phase_workouts_returns_404_for_missing_phase(client: TestClient) -> None:
    """GET /phases/{id}/workouts returns 404 when the phase does not exist."""
    response = client.get("/api/v1/resources/phases/999/workouts")

    assert response.status_code == 404


def test_get_workout_returns_workout(client: TestClient, db_session: Session) -> None:
    """GET /workouts/{id} returns the workout for a known ID."""
    phase = create_phase(db_session)
    workout = create_workout(
        db_session,
        phase,
        date_start=datetime(2026, 4, 12, 7, 0, tzinfo=UTC),
        done_date_start=datetime(2026, 4, 12, 8, 0, tzinfo=UTC),
        actual_duration_min=58.0,
        actual_distance_km=10.2,
        actual_training_load=390.0,
        actual_calories_burned_kcal=720.0,
        weighted_hrr_intensity_sum=145.5,
        actual_hrr_intensity=2.51,
        actual_rpe=7.0,
        status="Done",
    )

    response = client.get(f"/api/v1/resources/workouts/{workout.id}")

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
    assert data["tracked_sessions"] == []


def test_get_workout_returns_404_for_missing_workout(client: TestClient) -> None:
    """GET /workouts/{id} returns 404 when the workout does not exist."""
    response = client.get("/api/v1/resources/workouts/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout not found"


def test_get_workout_content_returns_workout_content(
    client: TestClient, db_session: Session
) -> None:
    """GET /workouts/{id}/content returns the content-focused workout payload."""
    phase = create_phase(db_session)
    workout = create_workout(
        db_session,
        phase,
        notion_page_content="Structured workout content",
        actual_duration_min=50.0,
        status="Done",
    )

    response = client.get(f"/api/v1/resources/workouts/{workout.id}/content")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workout.id
    assert data["notion_page_content"] == "Structured workout content"
    assert "tracked_sessions" not in data


def test_get_workout_content_returns_404_for_missing_workout(client: TestClient) -> None:
    """GET /workouts/{id}/content returns 404 when the workout does not exist."""
    response = client.get("/api/v1/resources/workouts/999/content")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout not found"


def test_get_workout_details_returns_workout_with_linked_sessions(
    client: TestClient, db_session: Session
) -> None:
    """GET /workouts/{id}/details returns linked tracked sessions."""
    phase = create_phase(db_session)
    workout = create_workout(db_session, phase, status="Done")
    session = create_tracked_session(
        db_session,
        workout=workout,
        name="Workout Detail Session",
        start=datetime(2026, 4, 12, 9, 0, tzinfo=UTC),
    )

    response = client.get(f"/api/v1/resources/workouts/{workout.id}/details")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workout.id
    assert [tracked["id"] for tracked in data["tracked_sessions"]] == [session.id]


def test_get_workout_details_returns_404_for_missing_workout(client: TestClient) -> None:
    """GET /workouts/{id}/details returns 404 when the workout does not exist."""
    response = client.get("/api/v1/resources/workouts/999/details")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout not found"


def test_get_workout_summary_returns_summary(client: TestClient, db_session: Session) -> None:
    """GET /workouts/{id}/summary returns the compact summary payload."""
    phase = create_phase(db_session)
    start = datetime(2026, 4, 12, 7, 0, tzinfo=UTC)
    end = datetime(2026, 4, 12, 8, 0, tzinfo=UTC)
    workout = create_workout(db_session, phase, name="Summary Workout", date_start=start)
    workout.date_end = end
    db_session.flush()

    response = client.get(f"/api/v1/resources/workouts/{workout.id}/summary")

    assert response.status_code == 200
    assert response.json() == {
        "id": workout.id,
        "name": "Summary Workout",
        "date_start": _iso_z(start),
        "date_end": _iso_z(end),
    }


def test_get_workout_summary_returns_404_for_missing_workout(client: TestClient) -> None:
    """GET /workouts/{id}/summary returns 404 when the workout does not exist."""
    response = client.get("/api/v1/resources/workouts/999/summary")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout not found"


def test_get_workout_sessions_returns_list(client: TestClient, db_session: Session) -> None:
    """GET /workouts/{id}/sessions returns all sessions linked to the workout."""
    phase = create_phase(db_session)
    workout = create_workout(db_session, phase)
    s1 = create_tracked_session(db_session, workout, name="Session A")
    s2 = create_tracked_session(db_session, workout, name="Session B")

    response = client.get(f"/api/v1/resources/workouts/{workout.id}/sessions")

    assert response.status_code == 200
    ids = {session["id"] for session in response.json()}
    assert ids == {s1.id, s2.id}


def test_get_workout_sessions_returns_404_for_missing_workout(client: TestClient) -> None:
    """GET /workouts/{id}/sessions returns 404 when the workout does not exist."""
    response = client.get("/api/v1/resources/workouts/999/sessions")

    assert response.status_code == 404


def test_get_session_returns_session(client: TestClient, db_session: Session) -> None:
    """GET /sessions/{id} returns the session for a known ID."""
    tracked = create_tracked_session(db_session)

    response = client.get(f"/api/v1/resources/sessions/{tracked.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tracked.id
    assert data["name"] == tracked.name


def test_get_session_returns_404_for_missing_session(client: TestClient) -> None:
    """GET /sessions/{id} returns 404 when the session does not exist."""
    response = client.get("/api/v1/resources/sessions/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_get_session_summary_returns_summary(client: TestClient, db_session: Session) -> None:
    """GET /sessions/{id}/summary returns the compact summary payload."""
    start = datetime(2026, 4, 12, 9, 0, tzinfo=UTC)
    tracked = create_tracked_session(db_session, name="Summary Session", start=start)
    tracked.end_end = datetime(2026, 4, 12, 10, 15, tzinfo=UTC)
    db_session.flush()

    response = client.get(f"/api/v1/resources/sessions/{tracked.id}/summary")

    assert response.status_code == 200
    assert response.json() == {
        "id": tracked.id,
        "name": "Summary Session",
        "source": None,
        "session_type": None,
        "start_start": _iso_z(start),
        "end_end": "2026-04-12T10:15:00Z",
    }


def test_get_session_summary_returns_404_for_missing_session(client: TestClient) -> None:
    """GET /sessions/{id}/summary returns 404 when the session does not exist."""
    response = client.get("/api/v1/resources/sessions/999/summary")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_get_recent_sessions_returns_sessions_within_window(
    client: TestClient, db_session: Session
) -> None:
    """GET /sessions/recent returns only sessions within the requested window."""
    now = datetime.now(tz=UTC)
    recent = create_tracked_session(
        db_session,
        start=now - timedelta(days=3),
        name="Recent Session",
    )
    create_tracked_session(db_session, start=now - timedelta(days=30), name="Old Session")

    response = client.get("/api/v1/resources/sessions/recent?days=14")

    assert response.status_code == 200
    ids = [session["id"] for session in response.json()]
    assert recent.id in ids
    for session in response.json():
        assert session["name"] != "Old Session"


def test_get_recent_sessions_default_window(client: TestClient, db_session: Session) -> None:
    """GET /sessions/recent uses a 14-day default when no days param is given."""
    now = datetime.now(tz=UTC)
    recent = create_tracked_session(
        db_session,
        start=now - timedelta(days=7),
        name="Recent Default",
    )

    response = client.get("/api/v1/resources/sessions/recent")

    assert response.status_code == 200
    ids = [session["id"] for session in response.json()]
    assert recent.id in ids


def test_get_recent_sessions_rejects_invalid_days(client: TestClient) -> None:
    """GET /sessions/recent returns 422 when days < 1."""
    response = client.get("/api/v1/resources/sessions/recent?days=0")

    assert response.status_code == 422
