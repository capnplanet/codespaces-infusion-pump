"""Pydantic schemas for patient domain objects."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PatientBase(BaseModel):
    demographics: dict[str, Any]


class PatientCreate(PatientBase):
    mrn: str = Field(min_length=1)


class PatientRead(PatientBase):
    id: int
    mrn: str
    created_at: datetime
    created_by: str

    model_config = {
        "from_attributes": True,
    }
