from sqlalchemy.orm import Session

from app.domain.models.workout import WorkoutData
from app.persistence.mapping import workout_mapper
from app.persistence.models.workout import Workout


class WorkoutRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_notion_id(self, notion_id: str) -> Workout | None:
        return self._session.query(Workout).filter_by(notion_id=notion_id).one_or_none()

    def upsert(self, data: WorkoutData, phase_id: int) -> Workout:
        existing = self.get_by_notion_id(data.notion_id)
        if existing is not None:
            workout_mapper.update_orm(existing, data, phase_id)
            return existing
        entity = workout_mapper.to_orm(data, phase_id)
        self._session.add(entity)
        self._session.flush()
        return entity
