from datetime import date

from pydantic import BaseModel


class WeeklyFeedbackData(BaseModel):
    notion_id: str
    week_start: date
    content: str
    phase_notion_id: str | None = None
