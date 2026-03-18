from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.base import Base


class WeeklyFeedback(Base):
    __tablename__ = "weekly_feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    notion_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    phase_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("phases.id"), nullable=True
    )
