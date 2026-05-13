"""Mapper for translating a NotionWorkout Pydantic model into a Workout SQLAlchemy entity."""

from __future__ import annotations

from datetime import UTC, datetime

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_workout import NotionWorkout
from ldk_athlete_ai_coach.db.models.training import Workout, WorkoutMetrics


def map_workout(
    source: NotionWorkout,
    entity: Workout | None = None,
    *,
    phase_id: int | None = None,
) -> Workout:
    """Map a validated :class:`NotionWorkout` onto a :class:`Workout` SQLAlchemy entity.

    Args:
        source: Validated Pydantic model extracted from the Notion Workouts database.
        entity: An existing :class:`Workout` instance to update in place.
            If ``None`` a new instance is created.
        phase_id: Resolved local primary key of the related :class:`Phase` row.
            Pass ``None`` when the relation is not yet resolved.

    Returns:
        The populated (new or updated) :class:`Workout` entity.

    """
    if entity is None:
        entity = Workout()

    # --- identifier fields (NotionSyncMixin) ---------------------------------
    entity.notion_page_id = source.notion_id
    entity.notion_url = source.url  # type: ignore[assignment]  # enforced by DB constraint
    entity.notion_page_content = source.notion_page_content

    # --- direct 1:1 field mappings -------------------------------------------
    entity.name = source.name
    entity.planned_date = source.planned_date
    entity.category = source.category
    entity.difficulty = source.difficulty
    entity.equipment = list(source.equipment)
    entity.impact = source.impact
    entity.metrics_to_record = list(source.metrics_to_record)
    entity.purpose = list(source.purpose)
    entity.primary_muscle_groups = list(source.primary_muscle_groups)
    entity.planned_distance_km = source.planned_distance_km
    entity.planned_duration_min = source.planned_duration_min
    entity.planned_rpe = source.planned_rpe
    entity.planned_week_number = source.planned_week_number
    entity.planned_week_start_date = source.planned_week_start_date
    entity.additional_info = source.additional_info
    entity.cancelled = source.cancelled
    entity.skipped = source.skipped
    entity.status = source.status

    # --- scalar foreign key fields -------------------------------------------
    # Callers that have already resolved the Notion phase page ID to a local DB
    # ID should pass the resolved value; otherwise the field is set to None.
    entity.phase_id = phase_id

    metrics = entity.metrics
    has_actual_metrics = any(
        value is not None
        for value in (
            source.actual_duration_min,
            source.actual_distance_km,
            source.actual_training_load,
            source.actual_calories_burned_kcal,
            source.weighted_hrr_intensity_sum,
            source.actual_hrr_intensity,
            source.actual_rpe,
            source.done_at,
            source.status,
            source.training_load_method,
        )
    )
    if has_actual_metrics or source.session_count > 0:
        if metrics is None:
            metrics = WorkoutMetrics(
                session_count=source.session_count,
                calculated_at=source.last_edited_time or datetime.now(tz=UTC),
                calculation_version=source.calculation_version,
            )
        metrics.session_count = source.session_count
        metrics.calculated_at = source.last_edited_time or datetime.now(tz=UTC)
        metrics.calculation_version = source.calculation_version
        metrics.actual_duration_min = source.actual_duration_min
        metrics.actual_distance_km = source.actual_distance_km
        metrics.actual_training_load = source.actual_training_load
        metrics.actual_calories_burned_kcal = source.actual_calories_burned_kcal
        metrics.weighted_hrr_intensity_sum = source.weighted_hrr_intensity_sum
        metrics.actual_hrr_intensity = source.actual_hrr_intensity
        metrics.actual_rpe = source.actual_rpe
        metrics.done_at = source.done_at
        metrics.training_load_method = source.training_load_method
        metrics.status = source.status
        entity.metrics = metrics
    else:
        entity.metrics = None

    return entity
