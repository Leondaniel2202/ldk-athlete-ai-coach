from datetime import date

from sqlalchemy.orm import Session

from app.domain.models.phase import PhaseData
from app.domain.models.training_session import TrainingSessionData
from app.domain.models.workout import WorkoutData
from app.persistence.models.training_session import TrainingSession
from app.persistence.repositories.phase_repository import PhaseRepository
from app.persistence.repositories.training_session_repository import (
    TrainingSessionRepository,
)
from app.persistence.repositories.workout_repository import WorkoutRepository


def _insert_phase_and_workout(db_session: Session) -> tuple[int, int]:
    phase_repo = PhaseRepository(db_session)
    phase = phase_repo.upsert(
        PhaseData(notion_id="notion-phase-1", name="Base Phase", order=1)
    )
    workout_repo = WorkoutRepository(db_session)
    workout = workout_repo.upsert(
        WorkoutData(
            notion_id="notion-workout-1",
            phase_notion_id="notion-phase-1",
            name="Long Run",
        ),
        phase.id,
    )
    return phase.id, workout.id


def test_insert_new_training_session(db_session: Session) -> None:
    _, workout_id = _insert_phase_and_workout(db_session)
    repo = TrainingSessionRepository(db_session)
    data = TrainingSessionData(
        notion_id="notion-session-1",
        workout_notion_id="notion-workout-1",
        date=date(2024, 1, 15),
        notes="Felt strong",
    )

    session = repo.upsert(data, workout_id)

    assert session.id is not None
    assert session.notion_id == "notion-session-1"
    assert session.date == date(2024, 1, 15)
    assert session.notes == "Felt strong"
    assert session.workout_id == workout_id


def test_update_existing_training_session(db_session: Session) -> None:
    _, workout_id = _insert_phase_and_workout(db_session)
    repo = TrainingSessionRepository(db_session)
    data = TrainingSessionData(
        notion_id="notion-session-1",
        workout_notion_id="notion-workout-1",
        date=date(2024, 1, 15),
    )
    repo.upsert(data, workout_id)

    updated = TrainingSessionData(
        notion_id="notion-session-1",
        workout_notion_id="notion-workout-1",
        date=date(2024, 1, 16),
        notes="Updated notes",
    )
    session = repo.upsert(updated, workout_id)

    assert session.date == date(2024, 1, 16)
    assert session.notes == "Updated notes"


def test_get_by_notion_id_found(db_session: Session) -> None:
    _, workout_id = _insert_phase_and_workout(db_session)
    repo = TrainingSessionRepository(db_session)
    data = TrainingSessionData(
        notion_id="notion-session-1",
        workout_notion_id="notion-workout-1",
        date=date(2024, 1, 15),
    )
    repo.upsert(data, workout_id)

    found = repo.get_by_notion_id("notion-session-1")

    assert found is not None
    assert found.notion_id == "notion-session-1"


def test_get_by_notion_id_not_found(db_session: Session) -> None:
    repo = TrainingSessionRepository(db_session)

    found = repo.get_by_notion_id("nonexistent-id")

    assert found is None


def test_idempotency_no_duplicates(db_session: Session) -> None:
    _, workout_id = _insert_phase_and_workout(db_session)
    repo = TrainingSessionRepository(db_session)
    data = TrainingSessionData(
        notion_id="notion-session-1",
        workout_notion_id="notion-workout-1",
        date=date(2024, 1, 15),
    )

    repo.upsert(data, workout_id)
    repo.upsert(data, workout_id)
    repo.upsert(data, workout_id)

    count = (
        db_session.query(TrainingSession)
        .filter_by(notion_id="notion-session-1")
        .count()
    )
    assert count == 1


def test_training_session_relationship_workout_id_assigned(
    db_session: Session,
) -> None:
    _, workout_id = _insert_phase_and_workout(db_session)
    repo = TrainingSessionRepository(db_session)
    data = TrainingSessionData(
        notion_id="notion-session-1",
        workout_notion_id="notion-workout-1",
        date=date(2024, 1, 15),
    )

    session = repo.upsert(data, workout_id)

    assert session.workout_id == workout_id
