"""Pump session management endpoints."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import get_current_user
from ..models import domain
from ..schemas import device as device_schema

router = APIRouter()


@router.post("/", response_model=device_schema.PumpSessionRead, status_code=status.HTTP_201_CREATED)
async def start_session(
    payload: device_schema.PumpSessionCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> device_schema.PumpSessionRead:
    patient = await db.get(domain.Patient, payload.patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    device_config = await db.get(domain.DeviceConfiguration, payload.device_configuration_id)
    if device_config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found")

    session = domain.PumpSession(
        patient_id=payload.patient_id,
        device_configuration_id=payload.device_configuration_id,
        clinician_target_map_mmhg=payload.clinician_target_map_mmhg,
        created_by=user["sub"],
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.post("/{session_id}/close", response_model=device_schema.PumpSessionRead)
async def close_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> device_schema.PumpSessionRead:
    session = await db.get(domain.PumpSession, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if session.ended_at is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Session already closed")

    now = datetime.now(tz=timezone.utc)
    session.ended_at = now
    session.status = "closed"
    session.modified_by = user["sub"]
    session.modified_at = now
    await db.commit()
    await db.refresh(session)
    return session
