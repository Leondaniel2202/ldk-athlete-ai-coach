from app.domain.models.training_session import TrainingSessionData
from app.persistence.models.training_session import TrainingSession


def to_orm(data: TrainingSessionData, workout_id: int) -> TrainingSession:
    return TrainingSession(
        notion_id=data.notion_id,
        workout_id=workout_id,
        date=data.date,
        notes=data.notes,
    )


def update_orm(
    entity: TrainingSession, data: TrainingSessionData, workout_id: int
) -> None:
    entity.workout_id = workout_id
    entity.date = data.date
    entity.notes = data.notes
