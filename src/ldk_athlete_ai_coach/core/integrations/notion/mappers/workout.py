"""Mapper for translating a NotionWorkout Pydantic model into a Workout SQLAlchemy entity."""

from __future__ import annotations

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_workout import NotionWorkout
from ldk_athlete_ai_coach.db.models.training import Workout


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

    # --- direct 1:1 field mappings -------------------------------------------
    entity.name = source.name
    entity.date_start = source.date_start
    entity.date_end = source.date_end
    entity.date_is_datetime = source.date_is_datetime
    entity.category = source.category
    entity.difficulty = source.difficulty
    entity.equipment = list(source.equipment)
    entity.impact = source.impact
    entity.metrics_to_record = list(source.metrics_to_record)
    entity.purpose = list(source.purpose)
    entity.primarily_used_muscle_group = list(source.primarily_used_muscle_group)
    entity.planned_distance_km = source.planned_distance_km
    entity.planned_duration_min = source.planned_duration_min
    entity.planned_rpe = source.planned_rpe
    entity.planned_week_number = source.planned_week_number
    entity.actual_rpe = source.actual_rpe
    entity.additional_info = source.additional_info
    entity.cancelled = source.cancelled
    entity.skipped = source.skipped

    # --- scalar foreign key fields -------------------------------------------
    # Callers that have already resolved the Notion phase page ID to a local DB
    # ID should pass the resolved value; otherwise the field is set to None.
    entity.phase_id = phase_id

    return entity
