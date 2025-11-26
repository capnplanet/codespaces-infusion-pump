"""Schemas for control configurations."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ControlParameterSetCreate(BaseModel):
    drug_library_id: int
    label: str
    limits: dict = Field(description="Hard safety limits and rate-of-change configurations")


class ControlParameterSetRead(BaseModel):
    id: int
    drug_library_id: int
    label: str
    limits: dict
    created_at: datetime

    class Config:
        from_attributes = True
