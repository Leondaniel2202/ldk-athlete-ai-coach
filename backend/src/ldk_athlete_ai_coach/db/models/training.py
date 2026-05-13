"""Training domain data models derived from the approved Notion databases."""

from __future__ import annotations

from datetime import UTC, date, datetime, time

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ldk_athlete_ai_coach.db.base import Base
from ldk_athlete_ai_coach.domain.enums.event import (
    EventPlanRole,
    EventPriority,
    EventStatus,
    EventType,
)
from ldk_athlete_ai_coach.domain.enums.phase import PhaseFocusTag, PhaseType
from ldk_athlete_ai_coach.domain.enums.session import SessionSource, SessionType
from ldk_athlete_ai_coach.domain.enums.status import WorkoutStatus
from ldk_athlete_ai_coach.domain.enums.workout import (
    MuscleGroup,
    WorkoutCategory,
    WorkoutEquipment,
    WorkoutPurpose,
)
from ldk_athlete_ai_coach.utils.date_utils import coerce_to_date


def _legacy_datetime(value: date | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.combine(value, time.min)


class TrainingEntityMixin:
    """Common columns used to map local rows back to their source system."""

    id: Mapped[int] = mapped_column(primary_key=True)
    notion_page_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    notion_url: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    notion_page_content: Mapped[str | None] = mapped_column(Text)


class Event(TrainingEntityMixin, Base):
    """Application-owned persisted event."""

    __tablename__ = "events"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[EventType] = mapped_column(
        String(64), nullable=False, default=EventType.UNKNOWN
    )
    sport: Mapped[WorkoutCategory] = mapped_column(
        String(64), nullable=False, default=WorkoutCategory.UNKNOWN
    )
    priority: Mapped[EventPriority] = mapped_column(
        String(16), nullable=False, default=EventPriority.UNKNOWN
    )
    status: Mapped[EventStatus] = mapped_column(
        String(32), nullable=False, default=EventStatus.UNKNOWN
    )
    event_format: Mapped[str | None] = mapped_column(Text)
    role_in_plan: Mapped[EventPlanRole | None] = mapped_column(String(32))
    target: Mapped[str | None] = mapped_column(Text)
    target_time_seconds: Mapped[int | None] = mapped_column(Integer)
    target_distance_km: Mapped[float | None] = mapped_column(Float)
    start_at: Mapped[datetime | None] = mapped_column("start_date_start", DateTime(timezone=True))
    end_at: Mapped[datetime | None] = mapped_column("end_date_start", DateTime(timezone=True))
    location: Mapped[str | None] = mapped_column("place_name", String(255))
    notes: Mapped[str | None] = mapped_column(Text)
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

    @property
    def start_date_start(self) -> datetime | None:
        return self.start_at

    @start_date_start.setter
    def start_date_start(self, value: datetime | None) -> None:
        self.start_at = value

    @property
    def start_date_end(self) -> None:
        return None

    @start_date_end.setter
    def start_date_end(self, _value: datetime | None) -> None:
        return None

    @property
    def start_date_is_datetime(self) -> bool:
        return self.start_at is not None

    @property
    def end_date_start(self) -> datetime | None:
        return self.end_at

    @end_date_start.setter
    def end_date_start(self, value: datetime | None) -> None:
        self.end_at = value

    @property
    def end_date_end(self) -> None:
        return None

    @end_date_end.setter
    def end_date_end(self, _value: datetime | None) -> None:
        return None

    @property
    def end_date_is_datetime(self) -> bool:
        return self.end_at is not None

    @property
    def place_name(self) -> str | None:
        return self.location

    @place_name.setter
    def place_name(self, value: str | None) -> None:
        self.location = value

    place_address = None
    place_latitude = None
    place_longitude = None
    place_google_place_id = None


class Plan(TrainingEntityMixin, Base):
    """Application-owned persisted training plan."""

    __tablename__ = "plans"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column("plan_goal", Text)
    start_date: Mapped[date | None] = mapped_column("start_date_start", Date)
    end_date: Mapped[date | None] = mapped_column("end_date_start", Date)

    events: Mapped[list[Event]] = relationship("Event", back_populates="plan")
    phases: Mapped[list[Phase]] = relationship("Phase", back_populates="plan")

    @property
    def plan_goal(self) -> str | None:
        return self.description

    @plan_goal.setter
    def plan_goal(self, value: str | None) -> None:
        self.description = value

    @property
    def constraints(self) -> None:
        return None

    @constraints.setter
    def constraints(self, _value: str | None) -> None:
        return None

    @property
    def rules_weekly_rhythm(self) -> None:
        return None

    @rules_weekly_rhythm.setter
    def rules_weekly_rhythm(self, _value: str | None) -> None:
        return None

    @property
    def start_date_start(self) -> datetime | None:
        return _legacy_datetime(self.start_date)

    @start_date_start.setter
    def start_date_start(self, value: datetime | date | None) -> None:
        coerced = coerce_to_date(value)
        self.start_date = coerced

    @property
    def start_date_end(self) -> None:
        return None

    @start_date_end.setter
    def start_date_end(self, _value: datetime | None) -> None:
        return None

    @property
    def start_date_is_datetime(self) -> bool:
        return False

    @start_date_is_datetime.setter
    def start_date_is_datetime(self, _value: bool) -> None:
        return None

    @property
    def end_date_start(self) -> datetime | None:
        return _legacy_datetime(self.end_date)

    @end_date_start.setter
    def end_date_start(self, value: datetime | date | None) -> None:
        coerced = coerce_to_date(value)
        self.end_date = coerced

    @property
    def end_date_end(self) -> None:
        return None

    @end_date_end.setter
    def end_date_end(self, _value: datetime | None) -> None:
        return None

    @property
    def end_date_is_datetime(self) -> bool:
        return False

    @end_date_is_datetime.setter
    def end_date_is_datetime(self, _value: bool) -> None:
        return None


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
    """Application-owned persisted training phase."""

    __tablename__ = "phases"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    phase_type: Mapped[PhaseType] = mapped_column(
        String(64), nullable=False, default=PhaseType.UNKNOWN
    )
    focus_tags: Mapped[list[PhaseFocusTag]] = mapped_column(
        MutableList.as_mutable(JSON), default=list, nullable=False
    )
    start_date: Mapped[date | None] = mapped_column("timeframe_start", Date)
    end_date: Mapped[date | None] = mapped_column("timeframe_end", Date)
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

    @property
    def weekly_structure(self) -> None:
        return None

    @weekly_structure.setter
    def weekly_structure(self, _value: str | None) -> None:
        return None

    @property
    def timeframe_start(self) -> datetime | None:
        return _legacy_datetime(self.start_date)

    @timeframe_start.setter
    def timeframe_start(self, value: datetime | date | None) -> None:
        coerced = coerce_to_date(value)
        self.start_date = coerced

    @property
    def timeframe_end(self) -> datetime | None:
        return _legacy_datetime(self.end_date)

    @timeframe_end.setter
    def timeframe_end(self, value: datetime | date | None) -> None:
        coerced = coerce_to_date(value)
        self.end_date = coerced

    @property
    def timeframe_is_datetime(self) -> bool:
        return False

    @timeframe_is_datetime.setter
    def timeframe_is_datetime(self, _value: bool) -> None:
        return None


class Workout(TrainingEntityMixin, Base):
    """Application-owned persisted planned workout."""

    __tablename__ = "workouts"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    planned_date: Mapped[date | None] = mapped_column("date_start", Date)
    category: Mapped[WorkoutCategory] = mapped_column(
        String(64), nullable=False, default=WorkoutCategory.UNKNOWN
    )
    difficulty: Mapped[str | None] = mapped_column(String(64))
    equipment: Mapped[list[WorkoutEquipment]] = mapped_column(
        MutableList.as_mutable(JSON), default=list, nullable=False
    )
    impact: Mapped[str | None] = mapped_column(String(32))
    metrics_to_record: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON),
        default=list,
        nullable=False,
    )
    purpose: Mapped[list[WorkoutPurpose]] = mapped_column(
        MutableList.as_mutable(JSON), default=list, nullable=False
    )
    primary_muscle_groups: Mapped[list[MuscleGroup]] = mapped_column(
        "primarily_used_muscle_group",
        MutableList.as_mutable(JSON),
        default=list,
        nullable=False,
    )
    planned_distance_km: Mapped[float | None] = mapped_column(Float)
    planned_duration_min: Mapped[float | None] = mapped_column(Float)
    planned_rpe: Mapped[float | None] = mapped_column(Float)
    _legacy_planned_training_load: Mapped[float | None] = mapped_column(
        "planned_training_load",
        Float,
    )
    planned_week_number: Mapped[float | None] = mapped_column(Float)
    planned_week_start_date: Mapped[date | None] = mapped_column(Date)
    additional_info: Mapped[str | None] = mapped_column(String(512))
    cancelled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    skipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    _legacy_status: Mapped[WorkoutStatus | None] = mapped_column("status", String(64))
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
    metrics: Mapped[WorkoutMetrics | None] = relationship(
        "WorkoutMetrics",
        back_populates="workout",
        cascade="all, delete-orphan",
        uselist=False,
    )

    def _ensure_metrics(self) -> WorkoutMetrics:
        if self.metrics is None:
            self.metrics = WorkoutMetrics(
                session_count=0,
                calculated_at=datetime.now(tz=UTC),
                calculation_version="legacy",
            )
        return self.metrics

    @property
    def date_start(self) -> datetime | None:
        return _legacy_datetime(self.planned_date)

    @date_start.setter
    def date_start(self, value: datetime | date | None) -> None:
        self.planned_date = coerce_to_date(value)

    @property
    def date_end(self) -> None:
        return None

    @date_end.setter
    def date_end(self, _value: datetime | None) -> None:
        return None

    @property
    def date_is_datetime(self) -> bool:
        return False

    @date_is_datetime.setter
    def date_is_datetime(self, _value: bool) -> None:
        return None

    @property
    def primarily_used_muscle_group(self) -> list[MuscleGroup]:
        return self.primary_muscle_groups

    @primarily_used_muscle_group.setter
    def primarily_used_muscle_group(self, value: list[MuscleGroup]) -> None:
        self.primary_muscle_groups = value

    @property
    def planned_training_load(self) -> float | None:
        if self._legacy_planned_training_load is not None:
            return self._legacy_planned_training_load
        if self.planned_duration_min is None or self.planned_rpe is None:
            return None
        return self.planned_duration_min * self.planned_rpe

    @planned_training_load.setter
    def planned_training_load(self, value: float | None) -> None:
        self._legacy_planned_training_load = value

    @property
    def actual_duration_min(self) -> float | None:
        return self.metrics.actual_duration_min if self.metrics is not None else None

    @actual_duration_min.setter
    def actual_duration_min(self, value: float | None) -> None:
        self._ensure_metrics().actual_duration_min = value

    @property
    def actual_distance_km(self) -> float | None:
        return self.metrics.actual_distance_km if self.metrics is not None else None

    @actual_distance_km.setter
    def actual_distance_km(self, value: float | None) -> None:
        self._ensure_metrics().actual_distance_km = value

    @property
    def actual_training_load(self) -> float | None:
        return self.metrics.actual_training_load if self.metrics is not None else None

    @actual_training_load.setter
    def actual_training_load(self, value: float | None) -> None:
        self._ensure_metrics().actual_training_load = value

    @property
    def actual_calories_burned_kcal(self) -> float | None:
        return self.metrics.actual_calories_burned_kcal if self.metrics is not None else None

    @actual_calories_burned_kcal.setter
    def actual_calories_burned_kcal(self, value: float | None) -> None:
        self._ensure_metrics().actual_calories_burned_kcal = value

    @property
    def weighted_hrr_intensity_sum(self) -> float | None:
        return self.metrics.weighted_hrr_intensity_sum if self.metrics is not None else None

    @weighted_hrr_intensity_sum.setter
    def weighted_hrr_intensity_sum(self, value: float | None) -> None:
        self._ensure_metrics().weighted_hrr_intensity_sum = value

    @property
    def actual_hrr_intensity(self) -> float | None:
        return self.metrics.actual_hrr_intensity if self.metrics is not None else None

    @actual_hrr_intensity.setter
    def actual_hrr_intensity(self, value: float | None) -> None:
        self._ensure_metrics().actual_hrr_intensity = value

    @property
    def actual_rpe(self) -> float | None:
        return self.metrics.actual_rpe if self.metrics is not None else None

    @actual_rpe.setter
    def actual_rpe(self, value: float | None) -> None:
        self._ensure_metrics().actual_rpe = value

    @property
    def done_date_start(self) -> datetime | None:
        return self.metrics.done_at if self.metrics is not None else None

    @done_date_start.setter
    def done_date_start(self, value: datetime | None) -> None:
        self._ensure_metrics().done_at = value

    @property
    def done_date_end(self) -> None:
        return None

    @done_date_end.setter
    def done_date_end(self, _value: datetime | None) -> None:
        return None

    @property
    def done_date_is_datetime(self) -> bool:
        return self.done_date_start is not None

    @done_date_is_datetime.setter
    def done_date_is_datetime(self, _value: bool) -> None:
        return None

    @property
    def status(self) -> WorkoutStatus | None:
        if self.metrics is not None and self.metrics.status is not None:
            return self.metrics.status
        return self._legacy_status

    @status.setter
    def status(self, value: WorkoutStatus | None) -> None:
        self._legacy_status = value
        self._ensure_metrics().status = value

    @property
    def training_load_method(self) -> str | None:
        return self.metrics.training_load_method if self.metrics is not None else None

    @training_load_method.setter
    def training_load_method(self, value: str | None) -> None:
        self._ensure_metrics().training_load_method = value


class WorkoutMetrics(Base):
    """Cached workout-level execution summary."""

    __tablename__ = "workout_metrics"

    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id"), primary_key=True)
    session_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    calculation_version: Mapped[str] = mapped_column(String(64), nullable=False)
    actual_duration_min: Mapped[float | None] = mapped_column(Float)
    actual_distance_km: Mapped[float | None] = mapped_column(Float)
    actual_training_load: Mapped[float | None] = mapped_column(Float)
    actual_calories_burned_kcal: Mapped[float | None] = mapped_column(Float)
    weighted_hrr_intensity_sum: Mapped[float | None] = mapped_column(Float)
    actual_hrr_intensity: Mapped[float | None] = mapped_column(Float)
    actual_rpe: Mapped[float | None] = mapped_column(Float)
    done_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    training_load_method: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[WorkoutStatus | None] = mapped_column(String(64))

    workout: Mapped[Workout] = relationship("Workout", back_populates="metrics")


class TrackedSession(TrainingEntityMixin, Base):
    """Application-owned persisted tracked session."""

    __tablename__ = "tracked_sessions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[SessionSource] = mapped_column(
        String(64), nullable=False, default=SessionSource.UNKNOWN
    )
    session_type: Mapped[SessionType] = mapped_column(
        String(128), nullable=False, default=SessionType.UNKNOWN
    )
    external_id: Mapped[str | None] = mapped_column(String(255))
    start_at: Mapped[datetime] = mapped_column(
        "start_start",
        DateTime(timezone=True),
        nullable=False,
    )
    end_at: Mapped[datetime | None] = mapped_column("end_start", DateTime(timezone=True))
    actual_rpe: Mapped[float | None] = mapped_column(Float)
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

    @property
    def start_start(self) -> datetime:
        return self.start_at

    @start_start.setter
    def start_start(self, value: datetime) -> None:
        self.start_at = value

    @property
    def start_end(self) -> None:
        return None

    @start_end.setter
    def start_end(self, _value: datetime | None) -> None:
        return None

    @property
    def start_is_datetime(self) -> bool:
        return True

    @start_is_datetime.setter
    def start_is_datetime(self, _value: bool) -> None:
        return None

    @property
    def end_start(self) -> datetime | None:
        return self.end_at

    @end_start.setter
    def end_start(self, value: datetime | None) -> None:
        self.end_at = value

    @property
    def end_end(self) -> None:
        return None

    @end_end.setter
    def end_end(self, _value: datetime | None) -> None:
        return None

    @property
    def end_is_datetime(self) -> bool:
        return self.end_at is not None

    @end_is_datetime.setter
    def end_is_datetime(self, _value: bool) -> None:
        return None


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
