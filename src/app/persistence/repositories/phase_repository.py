from sqlalchemy.orm import Session

from app.domain.models.phase import PhaseData
from app.persistence.mapping import phase_mapper
from app.persistence.models.phase import Phase


class PhaseRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_notion_id(self, notion_id: str) -> Phase | None:
        return self._session.query(Phase).filter_by(notion_id=notion_id).one_or_none()

    def upsert(self, data: PhaseData) -> Phase:
        existing = self.get_by_notion_id(data.notion_id)
        if existing is not None:
            phase_mapper.update_orm(existing, data)
            return existing
        entity = phase_mapper.to_orm(data)
        self._session.add(entity)
        self._session.flush()
        return entity
