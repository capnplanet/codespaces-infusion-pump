"""Schemas for drug library management."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DrugLibraryEntryCreate(BaseModel):
    drug_name: str
    concentration_mcg_per_ml: float
    min_rate_mcg_per_kg_min: float
    max_rate_mcg_per_kg_min: float
    max_delta_mcg_per_kg_min: float
    safety_notes: str | None = None


class DrugLibraryEntryRead(DrugLibraryEntryCreate):
    id: int
    created_at: datetime
    created_by: str

    model_config = {"from_attributes": True}
