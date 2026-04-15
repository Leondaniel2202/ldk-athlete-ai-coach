

from datetime import date

from pydantic import BaseModel


class ContextMetadataResponse(BaseModel):
    """Response metadata for the training-context endpoint."""

    as_of_date: date
    timezone: str