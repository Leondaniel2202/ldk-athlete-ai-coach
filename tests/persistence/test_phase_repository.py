from sqlalchemy.orm import Session

from app.domain.models.phase import PhaseData
from app.persistence.models.phase import Phase
from app.persistence.repositories.phase_repository import PhaseRepository


def test_insert_new_phase(db_session: Session) -> None:
    repo = PhaseRepository(db_session)
    data = PhaseData(notion_id="notion-phase-1", name="Base Phase", order=1)

    phase = repo.upsert(data)

    assert phase.id is not None
    assert phase.notion_id == "notion-phase-1"
    assert phase.name == "Base Phase"
    assert phase.order == 1


def test_update_existing_phase(db_session: Session) -> None:
    repo = PhaseRepository(db_session)
    data = PhaseData(notion_id="notion-phase-1", name="Base Phase", order=1)
    repo.upsert(data)

    updated = PhaseData(notion_id="notion-phase-1", name="Build Phase", order=2)
    phase = repo.upsert(updated)

    assert phase.name == "Build Phase"
    assert phase.order == 2


def test_get_by_notion_id_found(db_session: Session) -> None:
    repo = PhaseRepository(db_session)
    data = PhaseData(notion_id="notion-phase-1", name="Base Phase", order=1)
    repo.upsert(data)

    found = repo.get_by_notion_id("notion-phase-1")

    assert found is not None
    assert found.notion_id == "notion-phase-1"
    assert found.name == "Base Phase"


def test_get_by_notion_id_not_found(db_session: Session) -> None:
    repo = PhaseRepository(db_session)

    found = repo.get_by_notion_id("nonexistent-id")

    assert found is None


def test_idempotency_no_duplicates(db_session: Session) -> None:
    repo = PhaseRepository(db_session)
    data = PhaseData(notion_id="notion-phase-1", name="Base Phase", order=1)

    repo.upsert(data)
    repo.upsert(data)
    repo.upsert(data)

    count = db_session.query(Phase).filter_by(notion_id="notion-phase-1").count()
    assert count == 1
