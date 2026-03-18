from pydantic import BaseModel


class PhaseData(BaseModel):
    notion_id: str
    name: str
    order: int
