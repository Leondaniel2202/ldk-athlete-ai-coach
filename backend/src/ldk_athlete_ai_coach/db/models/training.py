"""Training domain data models derived from the approved Notion databases."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ldk_athlete_ai_coach.db.base import Base
from ldk_athlete_ai_coach.domain.enums.event import EventPriority, EventStatus, EventType
from ldk_athlete_ai_coach.domain.enums.phase import PhaseType
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus
from ldk_athlete_ai_coach.domain.enums.workout import WorkoutCategory


class TrainingEntityMixin:
    """Common columns used to map local rows back to their source system."""

    id: Mapped[int] = mapped_column(primary_key=True)
    notion_page_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    notion_url: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    notion_page_content: Mapped[str | None] = mapped_column(Text)


class Event(TrainingEntityMixin, Base):
    """Race, competition, benchmark, or milestone that anchors training."""

    __tablename__ = "events"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    event_type: Mapped[EventType] = mapped_column(String(64), nullable=False)
    sport: Mapped[WorkoutCategory] = mapped_column(String(64), nullable=False)

    priority: Mapped[EventPriority] = mapped_column(
        String(64),
        default=EventPriority.SECONDARY,
        nullable=False,
    )

    target_time_seconds: Mapped[int | None] = mapped_column(Integer)
    target_distance_km: Mapped[float | None] = mapped_column(Float)

    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    location: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)

    status: Mapped[EventStatus] = mapped_column(
        String(64),
        default=EventStatus.PLANNED,
        nullable=False,
    )

    plan_id: Mapped[int | None] = mapped_column(ForeignKey("plans.id"))
    race_workout_id: Mapped[int | None] = mapped_column(ForeignKey("workouts.id"))

    plan: Mapped[Plan | None] = relationship(
        "Plan",
        back_populates="events",
        foreign_keys=[plan_id],
    )
    race_workout: Mapped[Workout | None] = relationship(
        "Workout",
        back_populates="race_events",
        foreign_keys=[race_workout_id],
    )


class Plan(TrainingEntityMixin, Base):
    """Editable fields from the Notion Plans database."""

    __tablename__ = "plans"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    plan_goal: Mapped[str | None] = mapped_column(Text)
    constraints: Mapped[str | None] = mapped_column(Text)
    rules_weekly_rhythm: Mapped[str | None] = mapped_column(Text)
    start_date_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    start_date_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    start_date_is_datetime: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    end_date_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date_is_datetime: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    events: Mapped[list[Event]] = relationship(
        "Event",
        back_populates="plan",
        foreign_keys="Event.plan_id",
    )
    phases: Mapped[list[Phase]] = relationship("Phase", back_populates="plan")


class NutritionGuideline(TrainingEntityMixin, Base):
    """Editable fields from the Notion Nutrition Guidelines database."""

    __tablename__ = "nutrition_guidelines"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    goal: Mapped[str | None] = mapped_column(String(64))
    applies_to: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON), default=list, nullable=False
    )
    carb_strategy: Mapped[str | None] = mapped_column(Text)
    protein_target_g_per_kg: Mapped[str | None] = mapped_column(String(64))
    fat_target_g_per_kg: Mapped[str | None] = mapped_column(String(64))
    hydration_electrolytes: Mapped[str | None] = mapped_column(Text)
    supplements: Mapped[str | None] = mapped_column(Text)
    timing_rules: Mapped[str | None] = mapped_column(Text)

    phases: Mapped[list[Phase]] = relationship("Phase", back_populates="nutrition_guideline")


class Phase(TrainingEntityMixin, Base):
    """Editable fields from the Notion Phases database."""

    __tablename__ = "phases"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    phase_type: Mapped[PhaseType | None] = mapped_column(String(64))
    focus_tags: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON), default=list, nullable=False
    )
    weekly_structure: Mapped[str | None] = mapped_column(Text)
    timeframe_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    timeframe_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    timeframe_is_datetime: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    plan_id: Mapped[int | None] = mapped_column(ForeignKey("plans.id"))
    nutrition_guideline_id: Mapped[int | None] = mapped_column(
        ForeignKey("nutrition_guidelines.id")
    )

    plan: Mapped[Plan | None] = relationship("Plan", back_populates="phases")
    nutrition_guideline: Mapped[NutritionGuideline | None] = relationship(
        "NutritionGuideline",
        back_populates="phases",
    )
    workouts: Mapped[list[Workout]] = relationship("Workout", back_populates="phase")
    feedback_entries: Mapped[list[WeeklyFeedback]] = relationship(
        "WeeklyFeedback",
        back_populates="phase",
    )


class Workout(TrainingEntityMixin, Base):
    """Editable fields from the Notion Workouts database."""

    __tablename__ = "workouts"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_is_datetime: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    category: Mapped[WorkoutCategory | None] = mapped_column(String(64))
    difficulty: Mapped[str | None] = mapped_column(String(64))
    equipment: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON), default=list, nullable=False
    )
    impact: Mapped[str | None] = mapped_column(String(32))
    metrics_to_record: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON),
        default=list,
        nullable=False,
    )
    purpose: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON), default=list, nullable=False
    )
    primarily_used_muscle_group: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON),
        default=list,
        nullable=False,
    )
    planned_distance_km: Mapped[float | None] = mapped_column(Float)
    planned_duration_min: Mapped[float | None] = mapped_column(Float)
    planned_rpe: Mapped[float | None] = mapped_column(Float)
    planned_training_load: Mapped[float | None] = mapped_column(Float)
    planned_week_number: Mapped[float | None] = mapped_column(Float)
    planned_week_start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_duration_min: Mapped[float | None] = mapped_column(Float)
    actual_distance_km: Mapped[float | None] = mapped_column(Float)
    actual_training_load: Mapped[float | None] = mapped_column(Float)
    actual_calories_burned_kcal: Mapped[float | None] = mapped_column(Float)
    weighted_hrr_intensity_sum: Mapped[float | None] = mapped_column(Float)
    actual_hrr_intensity: Mapped[float | None] = mapped_column(Float)
    actual_rpe: Mapped[float | None] = mapped_column(Float)
    done_date_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    done_date_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    done_date_is_datetime: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[WorkoutStatus | None] = mapped_column(String(64))
    training_load_method: Mapped[str | None] = mapped_column(String(64))
    additional_info: Mapped[str | None] = mapped_column(String(512))
    cancelled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    skipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    phase_id: Mapped[int | None] = mapped_column(ForeignKey("phases.id"))

    phase: Mapped[Phase | None] = relationship("Phase", back_populates="workouts")
    race_events: Mapped[list[Event]] = relationship(
        "Event",
        back_populates="race_workout",
        foreign_keys="Event.race_workout_id",
    )
    tracked_sessions: Mapped[list[TrackedSession]] = relationship(
        "TrackedSession",
        back_populates="workout",
    )


class TrackedSession(TrainingEntityMixin, Base):
    """Editable fields from the Notion Tracked Sessions database."""

    __tablename__ = "tracked_sessions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str | None] = mapped_column(String(64))
    session_type: Mapped[str | None] = mapped_column(String(128))
    external_id: Mapped[str | None] = mapped_column(String(255))
    start_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    start_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    start_is_datetime: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    end_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_is_datetime: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    active_energy_kj: Mapped[float | None] = mapped_column(Float)
    active_energy_burned_kj: Mapped[float | None] = mapped_column(Float)
    avg_hr: Mapped[float | None] = mapped_column(Float)
    max_hr: Mapped[float | None] = mapped_column(Float)
    calories_kcal: Mapped[float | None] = mapped_column(Float)
    distance_km: Mapped[float | None] = mapped_column(Float)
    duration_min: Mapped[float | None] = mapped_column(Float)
    elevation_ascended_m: Mapped[float | None] = mapped_column(Float)
    elevation_descended_m: Mapped[float | None] = mapped_column(Float)
    intensity_kcal_per_hr_kg: Mapped[float | None] = mapped_column(Float)
    step_cadence_count_per_min: Mapped[float | None] = mapped_column(Float)
    steps: Mapped[float | None] = mapped_column(Float)
    workout_id: Mapped[int | None] = mapped_column(ForeignKey("workouts.id"))

    workout: Mapped[Workout | None] = relationship("Workout", back_populates="tracked_sessions")


class WeeklyFeedback(TrainingEntityMixin, Base):
    """Editable fields from the Notion Feedback database."""

    __tablename__ = "feedback"

    week: Mapped[str] = mapped_column(String(255), nullable=False)
    energy: Mapped[float | None] = mapped_column(Float)
    leg_freshness: Mapped[float | None] = mapped_column(Float)
    motivation: Mapped[float | None] = mapped_column(Float)
    recovery: Mapped[float | None] = mapped_column(Float)
    biggest_limitation: Mapped[str | None] = mapped_column(String(64))
    phase_id: Mapped[int | None] = mapped_column(ForeignKey("phases.id"))

    phase: Mapped[Phase | None] = relationship("Phase", back_populates="feedback_entries")


Feedback = WeeklyFeedback
