"""Factory helpers for building SQLAlchemy training model instances in tests."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.training import Phase, Plan, TrackedSession, Workout


def make_plan(
    db: Session,
    name: str = "Base Plan",
    *,
    notion_page_id: str | None = None,
    start_date_start: datetime | None = None,
    end_date_start: datetime | None = None,
) -> Plan:
    """Insert a minimal Plan into the database and return it."""
    plan = Plan(
        notion_page_id=notion_page_id or f"plan-{name}",
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


def make_phase(
    db: Session,
    plan: Plan,
    name: str = "Base Phase",
    *,
    notion_page_id: str | None = None,
    timeframe_start: datetime | None = None,
    timeframe_end: datetime | None = None,
) -> Phase:
    """Insert a minimal Phase into the database and return it."""
    phase = Phase(
        notion_page_id=notion_page_id or f"phase-{name}",
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


def make_workout(
    db: Session,
    phase: Phase,
    name: str = "Long Run",
    *,
    notion_page_id: str | None = None,
    date_start: datetime | None = None,
    done_date_start: datetime | None = None,
    notion_page_content: str = "Warm-up\nMain set\nCool-down",
    status: str | None = "Done",
    skipped: bool = False,
    cancelled: bool = False,
    planned_week_number: float | None = None,
    planned_training_load: float | None = 360.0,
    actual_training_load: float | None = None,
    actual_rpe: float | None = None,
) -> Workout:
    """Insert a minimal Workout into the database and return it."""
    workout = Workout(
        notion_page_id=notion_page_id or f"workout-{name}",
        notion_url=f"https://notion.so/workout-{name}",
        name=name,
        notion_page_content=notion_page_content,
        equipment=[],
        metrics_to_record=[],
        purpose=[],
        primarily_used_muscle_group=[],
        planned_training_load=planned_training_load,
        actual_training_load=actual_training_load,
        actual_rpe=actual_rpe,
        date_start=date_start,
        done_date_start=done_date_start,
        status=status,
        training_load_method="Weighted HRR",
        planned_week_number=planned_week_number,
        date_is_datetime=date_start is not None,
        cancelled=cancelled,
        skipped=skipped,
        done_date_is_datetime=done_date_start is not None,
        phase_id=phase.id,
    )
    db.add(workout)
    db.flush()
    return workout


def make_tracked_session(
    db: Session,
    workout: Workout | None = None,
    name: str = "Morning Run",
    *,
    notion_page_id: str | None = None,
    start: datetime | None = None,
) -> TrackedSession:
    """Insert a minimal TrackedSession into the database and return it."""
    tracked = TrackedSession(
        notion_page_id=notion_page_id or f"session-{name}",
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
