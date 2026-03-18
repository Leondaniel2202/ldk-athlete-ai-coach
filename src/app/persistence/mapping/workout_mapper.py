from app.domain.models.workout import WorkoutData
from app.persistence.models.workout import Workout


def to_orm(data: WorkoutData, phase_id: int) -> Workout:
    return Workout(
        notion_id=data.notion_id,
        phase_id=phase_id,
        name=data.name,
        description=data.description,
    )


def update_orm(entity: Workout, data: WorkoutData, phase_id: int) -> None:
    entity.phase_id = phase_id
    entity.name = data.name
    entity.description = data.description
