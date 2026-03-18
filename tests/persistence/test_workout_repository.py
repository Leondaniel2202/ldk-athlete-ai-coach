from sqlalchemy.orm import Session

from app.domain.models.phase import PhaseData
from app.domain.models.workout import WorkoutData
from app.persistence.models.workout import Workout
from app.persistence.repositories.phase_repository import PhaseRepository
from app.persistence.repositories.workout_repository import WorkoutRepository


def _insert_phase(db_session: Session, notion_id: str = "notion-phase-1") -> int:
    repo = PhaseRepository(db_session)
    phase = repo.upsert(PhaseData(notion_id=notion_id, name="Base Phase", order=1))
    return phase.id


def test_insert_new_workout(db_session: Session) -> None:
    phase_id = _insert_phase(db_session)
    repo = WorkoutRepository(db_session)
    data = WorkoutData(
        notion_id="notion-workout-1",
        phase_notion_id="notion-phase-1",
        name="Long Run",
        description="60 min easy run",
    )

    workout = repo.upsert(data, phase_id)

    assert workout.id is not None
    assert workout.notion_id == "notion-workout-1"
    assert workout.name == "Long Run"
    assert workout.description == "60 min easy run"
    assert workout.phase_id == phase_id


def test_update_existing_workout(db_session: Session) -> None:
    phase_id = _insert_phase(db_session)
    repo = WorkoutRepository(db_session)
    data = WorkoutData(
        notion_id="notion-workout-1",
        phase_notion_id="notion-phase-1",
        name="Long Run",
    )
    repo.upsert(data, phase_id)

    updated = WorkoutData(
        notion_id="notion-workout-1",
        phase_notion_id="notion-phase-1",
        name="Tempo Run",
        description="45 min at threshold",
    )
    workout = repo.upsert(updated, phase_id)

    assert workout.name == "Tempo Run"
    assert workout.description == "45 min at threshold"


def test_get_by_notion_id_found(db_session: Session) -> None:
    phase_id = _insert_phase(db_session)
    repo = WorkoutRepository(db_session)
    data = WorkoutData(
        notion_id="notion-workout-1",
        phase_notion_id="notion-phase-1",
        name="Long Run",
    )
    repo.upsert(data, phase_id)

    found = repo.get_by_notion_id("notion-workout-1")

    assert found is not None
    assert found.notion_id == "notion-workout-1"


def test_get_by_notion_id_not_found(db_session: Session) -> None:
    repo = WorkoutRepository(db_session)

    found = repo.get_by_notion_id("nonexistent-id")

    assert found is None


def test_idempotency_no_duplicates(db_session: Session) -> None:
    phase_id = _insert_phase(db_session)
    repo = WorkoutRepository(db_session)
    data = WorkoutData(
        notion_id="notion-workout-1",
        phase_notion_id="notion-phase-1",
        name="Long Run",
    )

    repo.upsert(data, phase_id)
    repo.upsert(data, phase_id)
    repo.upsert(data, phase_id)

    count = db_session.query(Workout).filter_by(notion_id="notion-workout-1").count()
    assert count == 1


def test_workout_relationship_phase_id_assigned(db_session: Session) -> None:
    phase_id = _insert_phase(db_session)
    repo = WorkoutRepository(db_session)
    data = WorkoutData(
        notion_id="notion-workout-1",
        phase_notion_id="notion-phase-1",
        name="Long Run",
    )

    workout = repo.upsert(data, phase_id)

    assert workout.phase_id == phase_id
