from datetime import date

from pydantic import BaseModel


class TrainingSessionData(BaseModel):
    notion_id: str
    workout_notion_id: str
    date: date
    notes: str | None = None
