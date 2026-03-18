from app.domain.models.weekly_feedback import WeeklyFeedbackData
from app.persistence.models.weekly_feedback import WeeklyFeedback


def to_orm(data: WeeklyFeedbackData, phase_id: int | None) -> WeeklyFeedback:
    return WeeklyFeedback(
        notion_id=data.notion_id,
        week_start=data.week_start,
        content=data.content,
        phase_id=phase_id,
    )


def update_orm(
    entity: WeeklyFeedback, data: WeeklyFeedbackData, phase_id: int | None
) -> None:
    entity.week_start = data.week_start
    entity.content = data.content
    entity.phase_id = phase_id
