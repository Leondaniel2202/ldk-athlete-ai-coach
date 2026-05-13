"""In-memory builders for training model unit tests."""

from __future__ import annotations

from datetime import UTC, datetime

from ldk_athlete_ai_coach.db.models.training import Phase, Plan, TrackedSession, Workout
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus


def build_plan(*, plan_id: int = 1, name: str = "Build Plan") -> Plan:
    return Plan(
        id=plan_id,
        notion_page_id=f"plan-{plan_id}",
        notion_url=f"https://notion.so/plan-{plan_id}",
        name=name,
        description="Race prep",
        start_date=datetime(2026, 4, 1, tzinfo=UTC).date(),
        end_date=datetime(2026, 5, 1, tzinfo=UTC).date(),
    )


def build_phase(
    *,
    phase_id: int = 2,
    plan: Plan | None,
    timeframe_start: datetime | None = None,
    timeframe_end: datetime | None = None,
) -> Phase:
    return Phase(
        id=phase_id,
        notion_page_id=f"phase-{phase_id}",
        notion_url=f"https://notion.so/phase-{phase_id}",
        name="Specific Build",
        notes=None,
        phase_type="Build",
        focus_tags=[],
        start_date=timeframe_start.date() if timeframe_start is not None else None,
        end_date=timeframe_end.date() if timeframe_end is not None else None,
        plan_id=plan.id if plan is not None else None,
        nutrition_guideline_id=None,
        plan=plan,
    )


def build_workout(
    *,
    workout_id: int,
    name: str,
    status: WorkoutStatus | None,
    phase: Phase | None,
    planned_week_start_date: datetime | None = None,
    planned_training_load: float | None = 100.0,
    actual_training_load: float | None = 50.0,
) -> Workout:
    return Workout(
        id=workout_id,
        notion_page_id=f"workout-{workout_id}",
        notion_url=f"https://notion.so/workout-{workout_id}",
        name=name,
        notion_page_content=f"Content for {name}",
        planned_date=None,
        category="Run",
        difficulty="Hard",
        equipment=[],
        impact=None,
        metrics_to_record=[],
        purpose=[],
        primary_muscle_groups=[],
        planned_distance_km=None,
        planned_duration_min=None,
        planned_rpe=None,
        planned_training_load=planned_training_load,
        planned_week_number=None,
        planned_week_start_date=planned_week_start_date.date() if planned_week_start_date else None,
        actual_duration_min=None,
        actual_distance_km=None,
        actual_training_load=actual_training_load,
        actual_calories_burned_kcal=None,
        weighted_hrr_intensity_sum=None,
        actual_hrr_intensity=None,
        actual_rpe=7.0,
        done_date_start=None,
        status=status,
        training_load_method=None,
        additional_info=None,
        cancelled=False,
        skipped=False,
        phase_id=phase.id if phase is not None else None,
        phase=phase,
        tracked_sessions=[],
    )


def build_session(
    *,
    session_id: int,
    workout_id: int | None,
    start_start: datetime | None = None,
) -> TrackedSession:
    return TrackedSession(
        id=session_id,
        notion_page_id=f"session-{session_id}",
        notion_url=f"https://notion.so/session-{session_id}",
        name=f"Session {session_id}",
        source="Apple Health",
        session_type="Running",
        external_id=None,
        start_at=start_start or datetime.now(tz=UTC),
        end_at=None,
        active_energy_kj=None,
        active_energy_burned_kj=None,
        avg_hr=None,
        max_hr=None,
        calories_kcal=None,
        distance_km=None,
        duration_min=None,
        elevation_ascended_m=None,
        elevation_descended_m=None,
        intensity_kcal_per_hr_kg=None,
        step_cadence_count_per_min=None,
        steps=None,
        workout_id=workout_id,
    )
