"""Tests for V1 context endpoints."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

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


def test_get_phase_context_returns_workout_centric_snapshot(
    client: TestClient,
    db_session: Session,
) -> None:
    """GET /context/phases/{id} returns the phase snapshot for a known phase."""
    now = datetime.now(tz=UTC)
    plan = create_plan(
        db_session,
        name="Active Plan",
        start_date_start=now - timedelta(days=30),
        end_date_start=now + timedelta(days=30),
    )
    phase = create_phase(
        db_session,
        name="Build Phase",
        plan=plan,
        timeframe_start=now - timedelta(days=8),
        timeframe_end=now + timedelta(days=14),
    )
    done_workout = create_workout(
        db_session,
        phase,
        name="Recent Workout",
        date_start=now - timedelta(days=2),
        done_date_start=now - timedelta(days=1),
        notion_page_content="Bike set",
        status="Done",
    )
    open_workout = create_workout(
        db_session,
        phase,
        name="Upcoming Workout",
        date_start=now + timedelta(days=1),
        notion_page_content="Run drills",
        status="Open",
    )
    tracked_session = create_tracked_session(
        db_session,
        done_workout,
        start=now - timedelta(days=1, hours=1),
        name="Recent Session",
    )

    response = client.get(f"/api/v1/context/phases/{phase.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["timezone"] == "UTC"
    assert data["plan_summary"]["id"] == plan.id
    assert data["phase"]["id"] == phase.id
    assert [workout["id"] for workout in data["open_workouts"]] == [open_workout.id]
    assert [workout["id"] for workout in data["done_workouts"]] == [done_workout.id]
    assert data["done_workouts"][0]["tracked_sessions"][0]["id"] == tracked_session.id
    assert data["adherence"] == {
        "planned_workouts": 2,
        "completed_workouts": 1,
        "skipped_workouts": 0,
        "unknown_workouts": 0,
        "completion_ratio": 0.5,
    }
    assert data["data_gaps"] == []


def test_get_phase_context_returns_sparse_response_when_no_workouts(
    client: TestClient,
    db_session: Session,
) -> None:
    """GET /context/phases/{id} returns empty workout collections when none exist."""
    now = datetime.now(tz=UTC)
    plan = create_plan(
        db_session,
        name="Sparse Plan",
        start_date_start=now - timedelta(days=7),
        end_date_start=now + timedelta(days=7),
    )
    phase = create_phase(
        db_session,
        name="Sparse Phase",
        plan=plan,
        timeframe_start=now - timedelta(days=3),
        timeframe_end=now + timedelta(days=3),
    )

    response = client.get(f"/api/v1/context/phases/{phase.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["open_workouts"] == []
    assert data["done_workouts"] == []
    assert data["weekly_metrics"] == []
    assert data["adherence"] == {
        "planned_workouts": 0,
        "completed_workouts": 0,
        "skipped_workouts": 0,
        "unknown_workouts": 0,
        "completion_ratio": None,
    }


def test_get_phase_context_reports_data_gaps(
    client: TestClient,
    db_session: Session,
) -> None:
    """GET /context/phases/{id} surfaces status and linkage gaps."""
    now = datetime.now(tz=UTC)
    plan = create_plan(
        db_session,
        name="Gap Plan",
        start_date_start=now - timedelta(days=7),
        end_date_start=now + timedelta(days=7),
    )
    phase = create_phase(
        db_session,
        name="Gap Phase",
        plan=plan,
        timeframe_start=now - timedelta(days=3),
        timeframe_end=now + timedelta(days=3),
    )
    create_workout(
        db_session,
        phase,
        name="Unknown Workout",
        date_start=now - timedelta(days=1),
        status="Unknown",
    )
    create_workout(
        db_session,
        phase,
        name="Missed Workout",
        date_start=now,
        status="Missed",
    )
    create_tracked_session(db_session, None, start=now, name="Unlinked Session")

    response = client.get(f"/api/v1/context/phases/{phase.id}")

    assert response.status_code == 200
    assert (
        "1 session within the phase timeframe is not linked to any workout."
        in response.json()["data_gaps"]
    )
    assert "1 workout in this phase has an unknown status." in response.json()["data_gaps"]
    assert "1 workout in this phase was missed." in response.json()["data_gaps"]


def test_get_phase_context_returns_404_for_missing_phase(client: TestClient) -> None:
    """GET /context/phases/{id} returns 404 when the phase does not exist."""
    response = client.get("/api/v1/context/phases/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Phase not found"


def test_get_phase_week_context_returns_week_snapshot(
    client: TestClient,
    db_session: Session,
) -> None:
    """GET /context/phases/{id}/weeks returns the requested phase-week snapshot."""
    plan = create_plan(
        db_session,
        name="Week Plan",
        start_date_start=datetime(2026, 4, 1, tzinfo=UTC),
        end_date_start=datetime(2026, 5, 1, tzinfo=UTC),
    )
    phase = create_phase(
        db_session,
        name="Week Phase",
        plan=plan,
        timeframe_start=datetime(2026, 4, 6, tzinfo=UTC),
        timeframe_end=datetime(2026, 5, 1, tzinfo=UTC),
    )
    week_start = datetime(2026, 4, 13, tzinfo=UTC)
    workout = create_workout(
        db_session,
        phase,
        name="Week Workout",
        date_start=week_start + timedelta(days=1),
        done_date_start=week_start + timedelta(days=1, hours=1),
        planned_week_start_date=week_start,
        planned_training_load=420.0,
        actual_training_load=410.0,
        actual_rpe=7.0,
        status="Done",
    )
    create_tracked_session(
        db_session,
        workout=workout,
        name="Week Session",
        start=week_start + timedelta(days=1, hours=1),
    )

    response = client.get(
        f"/api/v1/context/phases/{phase.id}/weeks",
        params={"week_start_date": week_start.isoformat()},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["plan_summary"]["id"] == plan.id
    assert data["phase_summary"]["id"] == phase.id
    assert data["metadata"]["phase_week_number"] == 2
    assert data["metadata"]["phase_week_start_date"] == _iso_z(week_start)
    assert data["workouts"][0]["id"] == workout.id
    assert data["metrics"]["timeframe_start"] == "2026-04-13"
    assert data["metrics"]["timeframe_end"] == "2026-04-19"
    assert data["adherence"] == {
        "planned_workouts": 1,
        "completed_workouts": 1,
        "skipped_workouts": 0,
        "unknown_workouts": 0,
        "completion_ratio": 1.0,
    }
    assert data["data_gaps"] == []


def test_get_phase_week_context_returns_404_for_missing_phase(client: TestClient) -> None:
    """GET /context/phases/{id}/weeks returns 404 when the phase does not exist."""
    response = client.get(
        "/api/v1/context/phases/999999/weeks",
        params={"week_start_date": "2026-04-14T00:00:00+00:00"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Phase not found"


def test_get_workout_context_returns_snapshot(client: TestClient, db_session: Session) -> None:
    """GET /context/workouts/{id} returns the workout snapshot for a known workout."""
    plan = create_plan(
        db_session,
        name="Workout Plan",
        start_date_start=datetime(2026, 4, 1, tzinfo=UTC),
        end_date_start=datetime(2026, 5, 1, tzinfo=UTC),
    )
    phase = create_phase(
        db_session,
        name="Workout Phase",
        plan=plan,
        timeframe_start=datetime(2026, 4, 7, tzinfo=UTC),
        timeframe_end=datetime(2026, 5, 1, tzinfo=UTC),
    )
    workout = create_workout(
        db_session,
        phase,
        name="Context Workout",
        date_start=datetime(2026, 4, 14, 7, 0, tzinfo=UTC),
        done_date_start=datetime(2026, 4, 14, 8, 0, tzinfo=UTC),
        actual_duration_min=55.0,
        actual_rpe=7.0,
        status="Done",
    )
    tracked_session = create_tracked_session(
        db_session,
        workout=workout,
        name="Context Session",
        start=datetime(2026, 4, 14, 8, 0, tzinfo=UTC),
    )

    response = client.get(f"/api/v1/context/workouts/{workout.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["timezone"] == "UTC"
    assert data["plan_summary"]["id"] == plan.id
    assert data["phase_summary"]["id"] == phase.id
    assert data["workout_status"] == "Done"
    assert data["workout_details"]["id"] == workout.id
    assert data["workout_details"]["tracked_sessions"][0]["id"] == tracked_session.id


def test_get_workout_context_returns_404_for_missing_workout(client: TestClient) -> None:
    """GET /context/workouts/{id} returns 404 when the workout does not exist."""
    response = client.get("/api/v1/context/workouts/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout not found"
