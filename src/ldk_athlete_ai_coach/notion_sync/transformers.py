"""Pure transform functions: Notion page dict → domain model kwargs dict.

Each ``transform_*`` function accepts a raw Notion page object (as returned by
the API) and returns a plain ``dict`` of keyword arguments that can be used to
construct or update the corresponding SQLAlchemy model instance.

Property extraction helpers are intentionally lenient: missing or ``None``
values are gracefully converted to ``None`` / empty lists rather than raising.
"""

from __future__ import annotations

from datetime import UTC, datetime

# ---------------------------------------------------------------------------
# Low-level property extraction helpers
# ---------------------------------------------------------------------------


def _plain_text(items: list[dict]) -> str:
    """Join rich-text / title array items into a plain string."""
    return "".join(item.get("plain_text", "") for item in items)


def _title(prop: dict) -> str:
    """Extract the plain-text value of a *title* property."""
    return _plain_text(prop.get("title", []))


def _rich_text(prop: dict) -> str | None:
    """Extract the plain-text value of a *rich_text* property, or ``None``."""
    text = _plain_text(prop.get("rich_text", []))
    return text or None


def _select(prop: dict) -> str | None:
    """Extract the name of a *select* property, or ``None``."""
    sel = prop.get("select")
    return sel["name"] if sel else None


def _multi_select(prop: dict) -> list[str]:
    """Extract the names from a *multi_select* property."""
    return [item["name"] for item in prop.get("multi_select", [])]


def _number(prop: dict) -> float | None:
    """Extract the value of a *number* property, or ``None``."""
    return prop.get("number")


def _checkbox(prop: dict) -> bool:
    """Extract the value of a *checkbox* property."""
    return bool(prop.get("checkbox", False))


def _url(prop: dict) -> str | None:
    """Extract the value of a *url* property, or ``None``."""
    return prop.get("url")


def _parse_notion_date(value: str | None) -> datetime | None:
    """Parse an ISO-8601 date/datetime string from Notion into a UTC datetime.

    Notion returns dates as ``"YYYY-MM-DD"`` and datetimes as
    ``"YYYY-MM-DDTHH:MM:SS.sss+HH:MM"`` (or ``Z``).  Both formats are handled.
    """
    if not value:
        return None
    try:
        if "T" in value:
            dt = datetime.fromisoformat(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            return dt
        else:
            # Date-only → midnight UTC
            parts = value.split("-")
            return datetime(int(parts[0]), int(parts[1]), int(parts[2]), tzinfo=UTC)
    except (ValueError, IndexError):
        return None


def _date_start(prop: dict) -> datetime | None:
    """Extract the *start* of a Notion *date* property."""
    d = prop.get("date") or {}
    return _parse_notion_date(d.get("start"))


def _date_end(prop: dict) -> datetime | None:
    """Extract the *end* of a Notion *date* property."""
    d = prop.get("date") or {}
    return _parse_notion_date(d.get("end"))


def _date_is_datetime(prop: dict) -> bool:
    """Return ``True`` if the Notion date property holds a datetime (not just a date)."""
    d = prop.get("date") or {}
    start = d.get("start", "") or ""
    return "T" in start


def _relation_ids(prop: dict) -> list[str]:
    """Return all related page IDs from a *relation* property."""
    return [item["id"] for item in prop.get("relation", [])]


def _relation_id(prop: dict) -> str | None:
    """Return the first related page ID from a *relation* property, or ``None``."""
    ids = _relation_ids(prop)
    return ids[0] if ids else None


def _page_id(page: dict) -> str:
    """Return the Notion page ID with hyphens removed (fits String(64) column)."""
    return page["id"].replace("-", "")


# ---------------------------------------------------------------------------
# Per-entity transformers
# ---------------------------------------------------------------------------
# Each function returns a plain dict suitable for **unpacking into a model
# constructor or update call.  Relation foreign-keys are intentionally *not*
# resolved here – the service layer resolves notion_page_id → local int id.
# ---------------------------------------------------------------------------


def transform_plan(page: dict) -> dict:
    """Transform a raw Notion Plans page into ``Plan`` model kwargs."""
    props = page.get("properties", {})
    return {
        "notion_page_id": _page_id(page),
        "notion_url": page.get("url", ""),
        "name": _title(props.get("Name", {})),
        "plan_goal": _rich_text(props.get("Goal", {})),
        "constraints": _rich_text(props.get("Constraints", {})),
        "rules_weekly_rhythm": _rich_text(props.get("Weekly Rhythm", {})),
        "start_date_start": _date_start(props.get("Start Date", {})),
        "start_date_end": _date_end(props.get("Start Date", {})),
        "start_date_is_datetime": _date_is_datetime(props.get("Start Date", {})),
        "end_date_start": _date_start(props.get("End Date", {})),
        "end_date_end": _date_end(props.get("End Date", {})),
        "end_date_is_datetime": _date_is_datetime(props.get("End Date", {})),
    }


def transform_nutrition_guideline(page: dict) -> dict:
    """Transform a raw Notion Nutrition Guidelines page into ``NutritionGuideline`` kwargs."""
    props = page.get("properties", {})
    return {
        "notion_page_id": _page_id(page),
        "notion_url": page.get("url", ""),
        "name": _title(props.get("Name", {})),
        "goal": _select(props.get("Goal", {})),
        "applies_to": _multi_select(props.get("Applies To", {})),
        "carb_strategy": _rich_text(props.get("Carb Strategy", {})),
        "protein_target_g_per_kg": _rich_text(props.get("Protein Target (g/kg)", {})),
        "fat_target_g_per_kg": _rich_text(props.get("Fat Target (g/kg)", {})),
        "hydration_electrolytes": _rich_text(props.get("Hydration & Electrolytes", {})),
        "supplements": _rich_text(props.get("Supplements", {})),
        "timing_rules": _rich_text(props.get("Timing Rules", {})),
    }


def transform_training_load(page: dict) -> dict:
    """Transform a raw Notion Training Load page into ``TrainingLoad`` kwargs."""
    props = page.get("properties", {})
    return {
        "notion_page_id": _page_id(page),
        "notion_url": page.get("url", ""),
        "name": _title(props.get("Name", {})),
        "impact": _select(props.get("Impact", {})),
        "min_load": _number(props.get("Min Load", {})),
        "max_load": _number(props.get("Max Load", {})),
        "typical_avg_rpe": _number(props.get("Typical Avg RPE", {})),
        "meaning": _rich_text(props.get("Meaning", {})),
    }


def transform_phase(page: dict) -> dict:
    """Transform a raw Notion Phases page into ``Phase`` kwargs.

    The ``plan_notion_id`` and ``nutrition_notion_id`` extras are raw Notion
    relation page IDs that the service layer resolves to local integer PKs.
    """
    props = page.get("properties", {})
    return {
        "notion_page_id": _page_id(page),
        "notion_url": page.get("url", ""),
        "name": _title(props.get("Name", {})),
        "notes": _rich_text(props.get("Notes", {})),
        "phase_type": _select(props.get("Phase Type", {})),
        "focus_tags": _multi_select(props.get("Focus Tags", {})),
        "weekly_structure": _rich_text(props.get("Weekly Structure", {})),
        "timeframe_start": _date_start(props.get("Timeframe", {})),
        "timeframe_end": _date_end(props.get("Timeframe", {})),
        "timeframe_is_datetime": _date_is_datetime(props.get("Timeframe", {})),
        # Relation stubs – resolved by the service layer
        "plan_notion_id": _relation_id(props.get("Plan", {})),
        "nutrition_notion_id": _relation_id(props.get("Nutrition Guideline", {})),
    }


def transform_workout(page: dict) -> dict:
    """Transform a raw Notion Workouts page into ``Workout`` kwargs.

    ``phase_notion_id`` is a raw Notion relation page ID resolved by the service.
    """
    props = page.get("properties", {})
    return {
        "notion_page_id": _page_id(page),
        "notion_url": page.get("url", ""),
        "name": _title(props.get("Name", {})),
        "date_start": _date_start(props.get("Date", {})),
        "date_end": _date_end(props.get("Date", {})),
        "date_is_datetime": _date_is_datetime(props.get("Date", {})),
        "category": _select(props.get("Category", {})),
        "difficulty": _select(props.get("Difficulty", {})),
        "equipment": _multi_select(props.get("Equipment", {})),
        "impact": _select(props.get("Impact", {})),
        "metrics_to_record": _multi_select(props.get("Metrics to Record", {})),
        "purpose": _multi_select(props.get("Purpose", {})),
        "primarily_used_muscle_group": _multi_select(props.get("Primarily Used Muscle Group", {})),
        "planned_distance_km": _number(props.get("Planned Distance (km)", {})),
        "planned_duration_min": _number(props.get("Planned Duration (min)", {})),
        "planned_rpe": _number(props.get("Planned RPE", {})),
        "planned_week_number": _number(props.get("Planned Week Number", {})),
        "actual_rpe": _number(props.get("Actual RPE", {})),
        "additional_info": _rich_text(props.get("Additional Info", {})),
        "cancelled": _checkbox(props.get("Cancelled", {})),
        "skipped": _checkbox(props.get("Skipped", {})),
        # Relation stub – resolved by the service layer
        "phase_notion_id": _relation_id(props.get("Phase", {})),
    }


def transform_event(page: dict) -> dict:
    """Transform a raw Notion Events page into ``Event`` kwargs.

    ``plan_notion_id`` and ``race_workout_notion_id`` are resolved by the service.
    """
    props = page.get("properties", {})
    return {
        "notion_page_id": _page_id(page),
        "notion_url": page.get("url", ""),
        "name": _title(props.get("Name", {})),
        "event_type": _select(props.get("Type", {})),
        "target": _rich_text(props.get("Target", {})),
        "event_format": _rich_text(props.get("Format", {})),
        "notes": _rich_text(props.get("Notes", {})),
        "priority": _select(props.get("Priority", {})),
        "start_date_start": _date_start(props.get("Start Date", {})),
        "start_date_end": _date_end(props.get("Start Date", {})),
        "start_date_is_datetime": _date_is_datetime(props.get("Start Date", {})),
        "end_date_start": _date_start(props.get("End Date", {})),
        "end_date_end": _date_end(props.get("End Date", {})),
        "end_date_is_datetime": _date_is_datetime(props.get("End Date", {})),
        "place_name": _rich_text(props.get("Place Name", {})),
        "place_address": _rich_text(props.get("Place Address", {})),
        "place_latitude": _number(props.get("Latitude", {})),
        "place_longitude": _number(props.get("Longitude", {})),
        "place_google_place_id": _rich_text(props.get("Google Place ID", {})),
        # Relation stubs – resolved by the service layer
        "plan_notion_id": _relation_id(props.get("Plan", {})),
        "race_workout_notion_id": _relation_id(props.get("Race Workout", {})),
    }


def transform_tracked_session(page: dict) -> dict:
    """Transform a raw Notion Tracked Sessions page into ``TrackedSession`` kwargs.

    ``workout_notion_id`` is resolved by the service layer.
    """
    props = page.get("properties", {})
    return {
        "notion_page_id": _page_id(page),
        "notion_url": page.get("url", ""),
        "name": _title(props.get("Name", {})),
        "source": _select(props.get("Source", {})),
        "session_type": _rich_text(props.get("Session Type", {})),
        "external_id": _rich_text(props.get("External ID", {})),
        "start_start": _date_start(props.get("Start", {})),
        "start_end": _date_end(props.get("Start", {})),
        "start_is_datetime": _date_is_datetime(props.get("Start", {})),
        "end_start": _date_start(props.get("End", {})),
        "end_end": _date_end(props.get("End", {})),
        "end_is_datetime": _date_is_datetime(props.get("End", {})),
        "active_energy_kj": _number(props.get("Active Energy (kJ)", {})),
        "active_energy_burned_kj": _number(props.get("Active Energy Burned (kJ)", {})),
        "avg_hr": _number(props.get("Avg HR", {})),
        "max_hr": _number(props.get("Max HR", {})),
        "calories_kcal": _number(props.get("Calories (kcal)", {})),
        "distance_km": _number(props.get("Distance (km)", {})),
        "duration_min": _number(props.get("Duration (min)", {})),
        "elevation_ascended_m": _number(props.get("Elevation Ascended (m)", {})),
        "elevation_descended_m": _number(props.get("Elevation Descended (m)", {})),
        "intensity_kcal_per_hr_kg": _number(props.get("Intensity (kcal/hr/kg)", {})),
        "step_cadence_count_per_min": _number(props.get("Step Cadence (count/min)", {})),
        "steps": _number(props.get("Steps", {})),
        # Relation stub – resolved by the service layer
        "workout_notion_id": _relation_id(props.get("Workout", {})),
    }


def transform_feedback(page: dict) -> dict:
    """Transform a raw Notion Feedback page into ``Feedback`` kwargs.

    ``phase_notion_id`` is resolved by the service layer.
    """
    props = page.get("properties", {})
    return {
        "notion_page_id": _page_id(page),
        "notion_url": page.get("url", ""),
        "week": _title(props.get("Week", {})),
        "energy": _number(props.get("Energy", {})),
        "leg_freshness": _number(props.get("Leg Freshness", {})),
        "motivation": _number(props.get("Motivation", {})),
        "recovery": _number(props.get("Recovery", {})),
        "biggest_limitation": _select(props.get("Biggest Limitation", {})),
        # Relation stub – resolved by the service layer
        "phase_notion_id": _relation_id(props.get("Phase", {})),
    }
