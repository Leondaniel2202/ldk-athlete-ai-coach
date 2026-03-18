from pydantic import BaseModel


class WorkoutData(BaseModel):
    notion_id: str
    phase_notion_id: str
    name: str
    description: str | None = None
