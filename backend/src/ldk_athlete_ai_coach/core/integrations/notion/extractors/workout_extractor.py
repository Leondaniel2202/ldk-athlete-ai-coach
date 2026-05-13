"""Extractor for Notion Workout database entries."""

from __future__ import annotations

from typing import Any

from ldk_athlete_ai_coach.core.integrations.notion.extractors import NotionExtractionError
from ldk_athlete_ai_coach.core.integrations.notion.extractors._helpers import (
    get_checkbox,
    get_date,
    get_first_relation,
    get_formula_date,
    get_formula_number,
    get_formula_string,
    get_multi_select,
    get_number,
    get_page_datetime,
    get_property_by_alias,
    get_rich_text,
    get_rollup_date,
    get_rollup_number,
    get_select,
    get_title,
    get_url,
)
from ldk_athlete_ai_coach.core.integrations.notion.schemas.notion_workout import NotionWorkout
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus
from ldk_athlete_ai_coach.domain.enums.workout import (
    MuscleGroup,
    WorkoutCategory,
    WorkoutEquipment,
    WorkoutPurpose,
)
from ldk_athlete_ai_coach.utils.date_utils import coerce_to_date


def extract_workout(raw_page: dict[str, Any]) -> NotionWorkout:
    """Convert a raw Notion Workout page object into a :class:`NotionWorkout` model.

    Args:
        raw_page: A single entry from the Notion Workouts database as returned by
            :meth:`~ldk_athlete_ai_coach.core.integrations.notion.client.NotionClient.iter_database_entries`.

    Returns:
        A validated :class:`NotionWorkout` instance.

    Raises:
        NotionExtractionError: If required fields are missing or the payload is malformed.

    """
    try:
        notion_id: str = raw_page["id"]
        props: dict[str, Any] = raw_page["properties"]

        name = get_title(props.get("Name", {}))
        if not name:
            raise NotionExtractionError(
                f"Workout page {notion_id!r} is missing required 'Name' property"
            )

        planned_date, _, _ = get_date(props.get("Planned Date", {}))
        done_at, _, _ = get_rollup_date(props.get("Done Date", {}))
        additional_info_prop = get_property_by_alias(props, "Additional Info")
        category = WorkoutCategory(get_select(props.get("Category", {})) or WorkoutCategory.UNKNOWN)
        planned_week_start_date = get_formula_date(props.get("Planned Week Startdate", {}))[0]
        if planned_week_start_date is None:
            raise NotionExtractionError(
                f"Workout page {notion_id!r} is missing required 'Planned Week Startdate' property"
            )
        planned_week_start_date_value = coerce_to_date(planned_week_start_date)
        assert planned_week_start_date_value is not None
        actual_duration_min = get_rollup_number(props.get("Actual Duration (min)", {}))
        actual_distance_km = get_rollup_number(props.get("Actual Distance", {}))
        actual_training_load = get_rollup_number(props.get("Actual Training Load", {}))
        actual_calories_burned_kcal = get_rollup_number(
            props.get("Actual calories burned (kcal)", {})
        )
        weighted_hrr_intensity_sum = get_rollup_number(
            props.get("Weighted HRR Intensity Sum", {})
        )
        actual_hrr_intensity = get_formula_number(props.get("Actual HRR Intensity", {}))
        actual_rpe = get_number(props.get("Actual RPE", {}))
        has_actual_metrics = any(
            value is not None
            for value in (
                actual_duration_min,
                actual_distance_km,
                actual_training_load,
                actual_calories_burned_kcal,
                weighted_hrr_intensity_sum,
                actual_hrr_intensity,
                actual_rpe,
                done_at,
            )
        )

        return NotionWorkout(
            notion_id=notion_id,
            name=name,
            planned_date=coerce_to_date(planned_date),
            category=category,
            difficulty=get_select(props.get("Difficulty", {})),
            equipment=[
                WorkoutEquipment(value)
                for value in get_multi_select(props.get("Equipment", {}))
            ],
            impact=get_select(props.get("Impact", {})),
            metrics_to_record=get_multi_select(
                get_property_by_alias(props, "Metrics to record", "Metrics to Record")
            ),
            purpose=[WorkoutPurpose(value) for value in get_multi_select(props.get("Purpose", {}))],
            primary_muscle_groups=[
                MuscleGroup(value)
                for value in get_multi_select(
                    get_property_by_alias(
                        props,
                        "Primarily used muscle group",
                        "Primarily Used Muscle Group",
                    )
                )
            ],
            planned_distance_km=get_number(props.get("Planned Distance (km)", {})),
            planned_duration_min=get_number(
                get_property_by_alias(props, "Planned duration (min)", "Planned Duration (min)")
            ),
            planned_rpe=get_number(props.get("Planned RPE", {})),
            planned_week_number=get_number(props.get("Planned Week Number", {})),
            planned_week_start_date=planned_week_start_date_value,
            actual_duration_min=actual_duration_min,
            actual_distance_km=actual_distance_km,
            actual_training_load=actual_training_load,
            actual_calories_burned_kcal=actual_calories_burned_kcal,
            weighted_hrr_intensity_sum=weighted_hrr_intensity_sum,
            actual_hrr_intensity=actual_hrr_intensity,
            actual_rpe=actual_rpe,
            done_at=done_at,
            session_count=1 if has_actual_metrics else 0,
            status=(
                WorkoutStatus(status_value)
                if (status_value := get_formula_string(props.get("Status", {})))
                else None
            ),
            training_load_method=get_formula_string(props.get("Training Load Method", {})),
            additional_info=get_url(additional_info_prop) or get_rich_text(additional_info_prop),
            cancelled=get_checkbox(props.get("Cancelled", {})),
            skipped=get_checkbox(props.get("Skipped", {})),
            phase_notion_id=get_first_relation(props.get("Phase", {})),
            created_time=get_page_datetime(raw_page, "created_time"),
            last_edited_time=get_page_datetime(raw_page, "last_edited_time"),
            archived=bool(raw_page.get("archived", False)),
            url=raw_page.get("url"),
        )
    except NotionExtractionError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise NotionExtractionError(f"Failed to extract Workout from Notion page: {exc}") from exc
