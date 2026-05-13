"""Mapper for translating a NotionSession Pydantic model into a TrackedSession entity."""

from __future__ import annotations

from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_session import NotionSession
from ldk_athlete_ai_coach.db.models.training import TrackedSession


def map_session(
    source: NotionSession,
    entity: TrackedSession | None = None,
    *,
    workout_id: int | None = None,
) -> TrackedSession:
    """Map a validated :class:`NotionSession` onto a :class:`TrackedSession` SQLAlchemy entity.

    Args:
        source: Validated Pydantic model extracted from the Notion Tracked Sessions database.
        entity: An existing :class:`TrackedSession` instance to update in place.
            If ``None`` a new instance is created.
        workout_id: Resolved local primary key of the related :class:`Workout` row.
            Pass ``None`` when the relation is not yet resolved.

    Returns:
        The populated (new or updated) :class:`TrackedSession` entity.

    """
    if entity is None:
        entity = TrackedSession()

    # --- identifier fields (NotionSyncMixin) ---------------------------------
    entity.notion_page_id = source.notion_id
    entity.notion_url = source.url  # type: ignore[assignment]  # enforced by DB constraint
    entity.notion_page_content = source.notion_page_content

    # --- direct 1:1 field mappings -------------------------------------------
    entity.name = source.name
    entity.source = source.source
    entity.session_type = source.session_type
    entity.external_id = source.external_id
    entity.start_at = source.start_at
    entity.end_at = source.end_at
    entity.actual_rpe = source.actual_rpe
    entity.active_energy_kj = source.active_energy_kj
    entity.active_energy_burned_kj = source.active_energy_burned_kj
    entity.avg_hr = source.avg_hr
    entity.max_hr = source.max_hr
    entity.calories_kcal = source.calories_kcal
    entity.distance_km = source.distance_km
    entity.duration_min = source.duration_min
    entity.elevation_ascended_m = source.elevation_ascended_m
    entity.elevation_descended_m = source.elevation_descended_m
    entity.intensity_kcal_per_hr_kg = source.intensity_kcal_per_hr_kg
    entity.step_cadence_count_per_min = source.step_cadence_count_per_min
    entity.steps = source.steps

    # --- scalar foreign key fields -------------------------------------------
    # Callers that have already resolved the Notion workout page ID to a local DB
    # ID should pass the resolved value; otherwise the field is set to None.
    entity.workout_id = workout_id

    return entity
