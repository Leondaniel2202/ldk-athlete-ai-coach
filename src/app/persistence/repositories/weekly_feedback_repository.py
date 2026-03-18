from sqlalchemy.orm import Session

from app.domain.models.weekly_feedback import WeeklyFeedbackData
from app.persistence.mapping import weekly_feedback_mapper
from app.persistence.models.weekly_feedback import WeeklyFeedback


class WeeklyFeedbackRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_notion_id(self, notion_id: str) -> WeeklyFeedback | None:
        return (
            self._session.query(WeeklyFeedback)
            .filter_by(notion_id=notion_id)
            .one_or_none()
        )

    def upsert(self, data: WeeklyFeedbackData, phase_id: int | None) -> WeeklyFeedback:
        existing = self.get_by_notion_id(data.notion_id)
        if existing is not None:
            weekly_feedback_mapper.update_orm(existing, data, phase_id)
            return existing
        entity = weekly_feedback_mapper.to_orm(data, phase_id)
        self._session.add(entity)
        self._session.flush()
        return entity
