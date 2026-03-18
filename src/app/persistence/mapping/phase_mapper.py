from app.domain.models.phase import PhaseData
from app.persistence.models.phase import Phase


def to_orm(data: PhaseData) -> Phase:
    return Phase(
        notion_id=data.notion_id,
        name=data.name,
        order=data.order,
    )


def update_orm(entity: Phase, data: PhaseData) -> None:
    entity.name = data.name
    entity.order = data.order
