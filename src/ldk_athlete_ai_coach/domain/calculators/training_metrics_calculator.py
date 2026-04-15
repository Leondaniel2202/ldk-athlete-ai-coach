from ldk_athlete_ai_coach.db.models.training import Workout
from ldk_athlete_ai_coach.domain.models.training_metrics import MetricAdherence, TrainingMetrics


class TrainingMetricsCalculator:
    """Calculates training metrics for a given workout and phase context."""

    def calculate(self, workouts: list[Workout]) -> TrainingMetrics:
        """Calculate training metrics based on the provided workouts."""
        planned_load = self._planned_training_load(workouts)
        actual_load = self._actual_training_load(workouts)

        adherence = None if planned_load == 0 else (actual_load / planned_load * 100)

        return TrainingMetrics(
            planned_training_load=planned_load,
            actual_training_load=actual_load,
            metric_adherence=[
                MetricAdherence(
                    metric_name="Training Load Adherence",
                    adherence_percentage=adherence,
                )
            ],
        )

    def _planned_training_load(self, workouts: list[Workout]) -> float:
        """Calculate the planned training load for a list of workouts."""
        return sum(
            workout.planned_training_load
            for workout in workouts
            if workout.planned_training_load is not None
        )

    def _actual_training_load(self, workouts: list[Workout]) -> float:
        """Calculate the actual training load for a list of workouts."""
        return sum(
            workout.actual_training_load
            for workout in workouts
            if workout.actual_training_load is not None
        )
