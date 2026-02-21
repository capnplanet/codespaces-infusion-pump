"""Device configuration endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import require_roles
from ..models import domain
from ..schemas import device as device_schema

router = APIRouter()


@router.post("/configurations", response_model=device_schema.DeviceConfigurationRead, status_code=status.HTTP_201_CREATED)
async def create_device_configuration(
    payload: device_schema.DeviceConfigurationCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles("admin")),
) -> device_schema.DeviceConfigurationRead:
    stmt = select(domain.DeviceConfiguration).where(domain.DeviceConfiguration.device_id == payload.device_id)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Device already configured")

    config = domain.DeviceConfiguration(
        device_id=payload.device_id,
        firmware_version=payload.firmware_version,
        gateway_version=payload.gateway_version,
        config_payload=payload.config_payload,
        created_by=user["sub"],
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return config


@router.get("/configurations/{config_id}", response_model=device_schema.DeviceConfigurationRead)
async def get_device_configuration(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles("admin", "clinician", "auditor")),
) -> device_schema.DeviceConfigurationRead:
    config = await db.get(domain.DeviceConfiguration, config_id)
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found")
    return config
