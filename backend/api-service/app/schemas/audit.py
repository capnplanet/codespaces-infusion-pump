"""Audit schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AuditEventCreate(BaseModel):
    event_type: str
    actor: str
    before: dict | None = None
    after: dict | None = None
    metadata: dict | None = None


class AuditEventRead(BaseModel):
    id: int
    event_type: str
    actor: str
    timestamp: datetime
    before: dict | None
    after: dict | None
    metadata: dict | None

    class Config:
        from_attributes = True
