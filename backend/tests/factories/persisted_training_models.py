"""Database-backed factories for training model tests."""

from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from ldk_athlete_ai_coach.db.models.training import Phase, Plan, TrackedSession, Workout


def create_plan(
    db: Session,
    name: str = "Base Plan",
    *,
    notion_page_id: str | None = None,
    description: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    start_date_start: datetime | None = None,
    end_date_start: datetime | None = None,
) -> Plan:
    """Insert a minimal Plan into the database and return it."""
    plan = Plan(
        notion_page_id=notion_page_id or f"plan-{name}",
        notion_url=f"https://notion.so/plan-{name}",
        name=name,
        description=description,
        start_date=start_date
        or (start_date_start.date() if start_date_start else date(2026, 1, 1)),
        end_date=end_date or (end_date_start.date() if end_date_start else date(2026, 12, 31)),
    )
    db.add(plan)
    db.flush()
    return plan


def create_phase(
    db: Session,
    name: str = "Base Phase",
    plan: Plan | None = None,
    *,
    notion_page_id: str | None = None,
    phase_type: str | None = None,
    timeframe_start: datetime | None = None,
    timeframe_end: datetime | None = None,
) -> Phase:
    """Insert a minimal Phase into the database and return it."""
    phase = Phase(
        notion_page_id=notion_page_id or f"phase-{name}",
        notion_url=f"https://notion.so/phase-{name}",
        name=name,
        phase_type=phase_type,
        focus_tags=[],
        timeframe_start=timeframe_start,
        timeframe_end=timeframe_end,
        timeframe_is_datetime=False,
        plan_id=plan.id if plan is not None else None,
    )
    db.add(phase)
    db.flush()
    return phase


def create_workout(
    db: Session,
    phase: Phase | None,
    name: str = "Long Run",
    *,
    notion_page_id: str | None = None,
    date_start: datetime | None = None,
    done_date_start: datetime | None = None,
    notion_page_content: str = "Warm-up\nMain set\nCool-down",
    status: str | None = "Done",
    category: str | None = None,
    skipped: bool = False,
    cancelled: bool = False,
    planned_week_number: float | None = None,
    planned_week_start_date: datetime | None = None,
    planned_training_load: float | None = 360.0,
    actual_training_load: float | None = None,
    actual_rpe: float | None = None,
    actual_duration_min: float | None = None,
    actual_distance_km: float | None = None,
    actual_calories_burned_kcal: float | None = None,
    weighted_hrr_intensity_sum: float | None = None,
    actual_hrr_intensity: float | None = None,
) -> Workout:
    """Insert a minimal Workout into the database and return it."""
    workout = Workout(
        notion_page_id=notion_page_id or f"workout-{name}",
        notion_url=f"https://notion.so/workout-{name}",
        name=name,
        notion_page_content=notion_page_content,
        category=category,
        equipment=[],
        metrics_to_record=[],
        purpose=[],
        primarily_used_muscle_group=[],
        planned_training_load=planned_training_load,
        actual_training_load=actual_training_load,
        actual_rpe=actual_rpe,
        actual_duration_min=actual_duration_min,
        actual_distance_km=actual_distance_km,
        actual_calories_burned_kcal=actual_calories_burned_kcal,
        weighted_hrr_intensity_sum=weighted_hrr_intensity_sum,
        actual_hrr_intensity=actual_hrr_intensity,
        date_start=date_start,
        done_date_start=done_date_start,
        status=status,
        training_load_method="Weighted HRR",
        planned_week_number=planned_week_number,
        planned_week_start_date=planned_week_start_date,
        date_is_datetime=date_start is not None,
        cancelled=cancelled,
        skipped=skipped,
        done_date_is_datetime=done_date_start is not None,
        phase_id=phase.id if phase is not None else None,
    )
    db.add(workout)
    db.flush()
    return workout


def create_tracked_session(
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
