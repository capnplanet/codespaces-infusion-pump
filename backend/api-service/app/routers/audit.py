"""Audit trail retrieval endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import require_roles
from ..models import domain

router = APIRouter()


@router.get("/events")
async def list_events(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles("admin", "auditor")),
) -> list[dict]:
    stmt = select(domain.AuditEvent).order_by(domain.AuditEvent.created_at.desc()).limit(limit)
    results = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": event.id,
            "created_at": event.created_at,
            "actor": event.actor,
            "action": event.action,
            "resource": event.resource,
            "metadata": event.event_metadata,
        }
        for event in results
    ]
