"""Tests for V1 dashboard endpoints."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.factories.persisted_training_models import (
    create_phase,
    create_plan,
    create_workout,
)

from ldk_athlete_ai_coach.utils.date_utils import get_week_start_for_date

pytestmark = pytest.mark.api


def test_get_dashboard_overview_returns_current_training_snapshot(
    client: TestClient,
    db_session: Session,
) -> None:
    """GET /dashboard/overview returns the current dashboard snapshot."""
    now = datetime.now(tz=UTC)
    week_start = get_week_start_for_date(now).replace(hour=0, minute=0, second=0, microsecond=0)
    plan = create_plan(
        db_session,
        name="API Dashboard Plan",
        start_date_start=now - timedelta(days=14),
        end_date_start=now + timedelta(days=14),
    )
    phase = create_phase(
        db_session,
        name="API Dashboard Phase",
        plan=plan,
        phase_type="Build",
        timeframe_start=now - timedelta(days=7),
        timeframe_end=now + timedelta(days=7),
    )
    open_workout = create_workout(
        db_session,
        phase,
        name="API Dashboard Run",
        status="Open",
        category="Run",
        planned_week_start_date=week_start,
        planned_training_load=80.0,
    )
    done_workout = create_workout(
        db_session,
        phase,
        name="API Dashboard Strength",
        status="Done",
        category="Strength",
        planned_week_start_date=week_start,
        planned_training_load=120.0,
    )

    response = client.get("/api/v1/dashboard/overview")

    assert response.status_code == 200
    data = response.json()
    assert data["athlete_name"] == "Leon"
    assert data["current_plan"]["id"] == plan.id
    assert data["current_phase"]["id"] == phase.id
    assert [workout["id"] for workout in data["weekly_outlook"]] == [
        done_workout.id,
        open_workout.id,
    ]
    assert data["overview"][0]["label"] == "Training focus"
    assert data["overview"][0]["value"] == "Build"
    assert data["overview"][1] == {
        "label": "This Week",
        "value": "2 Workouts",
        "detail": "1 Run workout, 1 Strength workout",
    }
    assert data["overview"][2] == {
        "label": "Execution",
        "value": "On Track",
        "detail": "1 done, 0 skipped, 1 open",
    }
    assert data["overview"][3] == {
        "label": "Planned Training Load",
        "value": "200.0",
        "detail": "Weekly load planned across all workouts with training load data",
    }


def test_get_dashboard_overview_returns_sparse_response(client: TestClient) -> None:
    """GET /dashboard/overview returns empty context when no active data exists."""
    response = client.get("/api/v1/dashboard/overview")

    assert response.status_code == 200
    data = response.json()
    assert data["current_plan"] is None
    assert data["current_phase"] is None
    assert data["weekly_outlook"] == []
    assert data["overview"][0]["value"] is None
    assert data["overview"][1]["value"] == "0 Workouts"
