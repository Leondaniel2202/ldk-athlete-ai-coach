"""Prompt-builder tests for AI phase-context analysis."""

from __future__ import annotations

from datetime import date

from ldk_athlete_ai_coach.ai.prompts.phase_context import build_analyze_phase_context_prompt
from ldk_athlete_ai_coach.api.v1.schemas.adherence import WorkoutAdherenceSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.common import ContextMetadataResponse
from ldk_athlete_ai_coach.api.v1.schemas.metrics import TrainingMetricsResponse
from ldk_athlete_ai_coach.api.v1.schemas.phase_context import PhaseContextResponse
from ldk_athlete_ai_coach.api.v1.schemas.phases import PhaseResponse
from ldk_athlete_ai_coach.api.v1.schemas.plans import PlanSummaryResponse
from ldk_athlete_ai_coach.api.v1.schemas.sessions import SessionResponse
from ldk_athlete_ai_coach.api.v1.schemas.workouts import (
    WorkoutContentResponse,
    WorkoutDetailResponse,
)
from ldk_athlete_ai_coach.domain.enums.status import PhaseStatus, WorkoutStatus
from ldk_athlete_ai_coach.domain.models.training_metrics import TrainingMetrics


def _context() -> PhaseContextResponse:
    phase = PhaseResponse(
        id=2,
        notion_page_id="phase-2",
        notion_url="https://notion.so/phase-2",
        name="Hyrox Specific",
        notes="More threshold work.",
        phase_type="Build",
        focus_tags=["hyrox", "running"],
        weekly_structure="2 quality sessions",
        timeframe_start=None,
        timeframe_end=None,
        timeframe_is_datetime=False,
        plan_id=1,
        nutrition_guideline_id=None,
    )
    open_workout = WorkoutContentResponse(
        id=3,
        notion_page_id="workout-3",
        notion_url="https://notion.so/workout-3",
        name="Compromised Run",
        date_start=None,
        date_end=None,
        date_is_datetime=False,
        category="Run",
        difficulty="Hard",
        equipment=["Sled"],
        impact="High",
        metrics_to_record=["HR"],
        purpose=["Specificity"],
        primarily_used_muscle_group=["Legs"],
        planned_distance_km=None,
        planned_duration_min=45.0,
        planned_rpe=8.0,
        planned_training_load=360.0,
        planned_week_number=4.0,
        actual_duration_min=None,
        actual_distance_km=None,
        actual_training_load=None,
        actual_calories_burned_kcal=None,
        weighted_hrr_intensity_sum=None,
        actual_hrr_intensity=None,
        actual_rpe=None,
        done_date_start=None,
        done_date_end=None,
        done_date_is_datetime=False,
        status="Open",
        training_load_method="Weighted HRR",
        additional_info=None,
        cancelled=False,
        skipped=False,
        phase_id=2,
        notion_page_content="Warm up, then 6 x 1km compromised efforts.",
    )
    session = SessionResponse(
        id=4,
        notion_page_id="session-4",
        notion_url="https://notion.so/session-4",
        name="Brick Session",
        source="Garmin",
        session_type="Run",
        external_id=None,
        start_start=None,
        start_end=None,
        start_is_datetime=False,
        end_start=None,
        end_end=None,
        end_is_datetime=False,
        active_energy_kj=None,
        active_energy_burned_kj=None,
        avg_hr=152.0,
        max_hr=None,
        calories_kcal=None,
        distance_km=8.0,
        duration_min=42.0,
        elevation_ascended_m=None,
        elevation_descended_m=None,
        intensity_kcal_per_hr_kg=None,
        step_cadence_count_per_min=None,
        steps=None,
        workout_id=5,
    )
    done_workout = WorkoutDetailResponse(
        **open_workout.model_dump(exclude={"id", "name", "status"}),
        id=5,
        name="Threshold Session",
        status="Done",
        tracked_sessions=[session],
    )
    return PhaseContextResponse(
        metadata=ContextMetadataResponse(as_of_date=date(2026, 4, 12), timezone="UTC"),
        plan_summary=PlanSummaryResponse(
            id=1,
            name="Race Build",
            plan_goal="Prepare for race day.",
            start_date_start=None,
            end_date_end=None,
        ),
        phase_status=PhaseStatus.ACTIVE,
        phase=phase,
        open_workouts=[open_workout],
        done_workouts=[done_workout],
        weekly_metrics=[
            TrainingMetricsResponse(
                timeframe_start=date(2026, 4, 7),
                timeframe_end=date(2026, 4, 13),
                training_metrics=TrainingMetrics(
                    planned_training_load=360.0,
                    actual_training_load=300.0,
                    metric_adherence=[],
                    included_statuses={WorkoutStatus.DONE},
                ),
            )
        ],
        adherence=WorkoutAdherenceSummaryResponse(
            planned_workouts=3,
            completed_workouts=2,
            skipped_workouts=0,
            unknown_workouts=0,
            completion_ratio=2 / 3,
        ),
        data_gaps=[
            (
                "No active phase matched the current date; using the latest phase "
                "for the selected plan instead."
            )
        ],
    )


def test_prompt_builder_includes_entity_names_page_content_and_data_gaps() -> None:
    """Prompt builder includes the synced context details that the model must ground on."""
    messages = build_analyze_phase_context_prompt(_context())

    assert messages[0]["role"] == "system"
    assert "Use only the provided context." in messages[0]["content"]
    user_content = messages[1]["content"]
    assert "Race Build" in user_content
    assert "Hyrox Specific" in user_content
    assert "Compromised Run" in user_content
    assert "Warm up, then 6 x 1km compromised efforts." in user_content
    assert "Brick Session" in user_content
    assert "No active phase matched the current date" in user_content


def test_prompt_builder_includes_optional_instruction() -> None:
    """Prompt builder appends the optional user instruction when provided."""
    messages = build_analyze_phase_context_prompt(
        _context(),
        instruction="Focus on recovery and intensity distribution.",
    )

    assert (
        "Additional instruction: Focus on recovery and intensity distribution."
        in messages[1]["content"]
    )
    assert "confidence score" not in messages[1]["content"]
