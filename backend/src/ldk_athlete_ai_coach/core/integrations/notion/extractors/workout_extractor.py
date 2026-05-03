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
from ldk_athlete_ai_coach.domain.enums.workout import WorkoutCategory


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

        date_start, date_end, date_is_datetime = get_date(props.get("Planned Date", {}))
        done_date_start, done_date_end, done_date_is_datetime = get_rollup_date(
            props.get("Done Date", {})
        )
        additional_info_prop = get_property_by_alias(props, "Additional Info")
        category = (
            WorkoutCategory(category_value)
            if (category_value := get_select(props.get("Category", {})))
            else None
        )

        return NotionWorkout(
            notion_id=notion_id,
            name=name,
            date_start=date_start,
            date_end=date_end,
            date_is_datetime=date_is_datetime,
            category=category,
            difficulty=get_select(props.get("Difficulty", {})),
            equipment=get_multi_select(props.get("Equipment", {})),
            impact=get_select(props.get("Impact", {})),
            metrics_to_record=get_multi_select(
                get_property_by_alias(props, "Metrics to record", "Metrics to Record")
            ),
            purpose=get_multi_select(props.get("Purpose", {})),
            primarily_used_muscle_group=get_multi_select(
                get_property_by_alias(
                    props,
                    "Primarily used muscle group",
                    "Primarily Used Muscle Group",
                )
            ),
            planned_distance_km=get_number(props.get("Planned Distance (km)", {})),
            planned_duration_min=get_number(
                get_property_by_alias(props, "Planned duration (min)", "Planned Duration (min)")
            ),
            planned_rpe=get_number(props.get("Planned RPE", {})),
            planned_training_load=get_formula_number(props.get("Planned Training Load", {})),
            planned_week_number=get_number(props.get("Planned Week Number", {})),
            planned_week_start_date=get_formula_date(props.get("Planned Week Startdate", {}))[0],
            actual_duration_min=get_rollup_number(props.get("Actual Duration (min)", {})),
            actual_distance_km=get_rollup_number(props.get("Actual Distance", {})),
            actual_training_load=get_rollup_number(props.get("Actual Training Load", {})),
            actual_calories_burned_kcal=get_rollup_number(
                props.get("Actual calories burned (kcal)", {})
            ),
            weighted_hrr_intensity_sum=get_rollup_number(
                props.get("Weighted HRR Intensity Sum", {})
            ),
            actual_hrr_intensity=get_formula_number(props.get("Actual HRR Intensity", {})),
            actual_rpe=get_number(props.get("Actual RPE", {})),
            done_date_start=done_date_start,
            done_date_end=done_date_end,
            done_date_is_datetime=done_date_is_datetime,
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
