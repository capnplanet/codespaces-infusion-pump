"""Schemas for ML model registry endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ModelVersionCreate(BaseModel):
    registry_id: str
    version: str
    dataset_hash: str
    validation_report_path: str
    acceptance_summary: dict


class ModelVersionRead(ModelVersionCreate):
    id: int
    created_at: datetime
    created_by: str

    model_config = {"from_attributes": True}
