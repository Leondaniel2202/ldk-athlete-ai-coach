from datetime import date

from sqlalchemy.orm import Session

from app.domain.models.phase import PhaseData
from app.domain.models.weekly_feedback import WeeklyFeedbackData
from app.persistence.models.weekly_feedback import WeeklyFeedback
from app.persistence.repositories.phase_repository import PhaseRepository
from app.persistence.repositories.weekly_feedback_repository import (
    WeeklyFeedbackRepository,
)


def _insert_phase(db_session: Session, notion_id: str = "notion-phase-1") -> int:
    repo = PhaseRepository(db_session)
    phase = repo.upsert(PhaseData(notion_id=notion_id, name="Base Phase", order=1))
    return phase.id


def test_insert_new_weekly_feedback(db_session: Session) -> None:
    phase_id = _insert_phase(db_session)
    repo = WeeklyFeedbackRepository(db_session)
    data = WeeklyFeedbackData(
        notion_id="notion-feedback-1",
        week_start=date(2024, 1, 8),
        content="Great week overall",
        phase_notion_id="notion-phase-1",
    )

    feedback = repo.upsert(data, phase_id)

    assert feedback.id is not None
    assert feedback.notion_id == "notion-feedback-1"
    assert feedback.week_start == date(2024, 1, 8)
    assert feedback.content == "Great week overall"
    assert feedback.phase_id == phase_id


def test_insert_weekly_feedback_without_phase(db_session: Session) -> None:
    repo = WeeklyFeedbackRepository(db_session)
    data = WeeklyFeedbackData(
        notion_id="notion-feedback-standalone",
        week_start=date(2024, 1, 8),
        content="Standalone feedback",
    )

    feedback = repo.upsert(data, None)

    assert feedback.id is not None
    assert feedback.phase_id is None


def test_update_existing_weekly_feedback(db_session: Session) -> None:
    phase_id = _insert_phase(db_session)
    repo = WeeklyFeedbackRepository(db_session)
    data = WeeklyFeedbackData(
        notion_id="notion-feedback-1",
        week_start=date(2024, 1, 8),
        content="Initial feedback",
        phase_notion_id="notion-phase-1",
    )
    repo.upsert(data, phase_id)

    updated = WeeklyFeedbackData(
        notion_id="notion-feedback-1",
        week_start=date(2024, 1, 8),
        content="Updated feedback",
        phase_notion_id="notion-phase-1",
    )
    feedback = repo.upsert(updated, phase_id)

    assert feedback.content == "Updated feedback"


def test_get_by_notion_id_found(db_session: Session) -> None:
    phase_id = _insert_phase(db_session)
    repo = WeeklyFeedbackRepository(db_session)
    data = WeeklyFeedbackData(
        notion_id="notion-feedback-1",
        week_start=date(2024, 1, 8),
        content="Great week",
        phase_notion_id="notion-phase-1",
    )
    repo.upsert(data, phase_id)

    found = repo.get_by_notion_id("notion-feedback-1")

    assert found is not None
    assert found.notion_id == "notion-feedback-1"


def test_get_by_notion_id_not_found(db_session: Session) -> None:
    repo = WeeklyFeedbackRepository(db_session)

    found = repo.get_by_notion_id("nonexistent-id")

    assert found is None


def test_idempotency_no_duplicates(db_session: Session) -> None:
    phase_id = _insert_phase(db_session)
    repo = WeeklyFeedbackRepository(db_session)
    data = WeeklyFeedbackData(
        notion_id="notion-feedback-1",
        week_start=date(2024, 1, 8),
        content="Great week",
        phase_notion_id="notion-phase-1",
    )

    repo.upsert(data, phase_id)
    repo.upsert(data, phase_id)
    repo.upsert(data, phase_id)

    count = (
        db_session.query(WeeklyFeedback)
        .filter_by(notion_id="notion-feedback-1")
        .count()
    )
    assert count == 1


def test_weekly_feedback_relationship_phase_id_assigned(db_session: Session) -> None:
    phase_id = _insert_phase(db_session)
    repo = WeeklyFeedbackRepository(db_session)
    data = WeeklyFeedbackData(
        notion_id="notion-feedback-1",
        week_start=date(2024, 1, 8),
        content="Great week",
        phase_notion_id="notion-phase-1",
    )

    feedback = repo.upsert(data, phase_id)

    assert feedback.phase_id == phase_id
