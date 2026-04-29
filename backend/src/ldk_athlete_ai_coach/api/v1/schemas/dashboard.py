"""Pydantic response models for the training domain."""

from __future__ import annotations

from pydantic import BaseModel

class DashboardHeaderResponse(BaseModel):

class DashboardReponse(BaseModel):
    """Summary of workout adherence in a reporting window."""

       header:  
