from sqlalchemy.orm import Session

from app.domain.models.training_session import TrainingSessionData
from app.persistence.mapping import training_session_mapper
from app.persistence.models.training_session import TrainingSession


class TrainingSessionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_notion_id(self, notion_id: str) -> TrainingSession | None:
        return (
            self._session.query(TrainingSession)
            .filter_by(notion_id=notion_id)
            .one_or_none()
        )

    def upsert(self, data: TrainingSessionData, workout_id: int) -> TrainingSession:
        existing = self.get_by_notion_id(data.notion_id)
        if existing is not None:
            training_session_mapper.update_orm(existing, data, workout_id)
            return existing
        entity = training_session_mapper.to_orm(data, workout_id)
        self._session.add(entity)
        self._session.flush()
        return entity
