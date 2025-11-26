"""Schemas for device configurations and pump sessions."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DeviceConfigurationCreate(BaseModel):
    device_id: str
    firmware_version: str
    gateway_version: str
    config_payload: dict


class DeviceConfigurationRead(DeviceConfigurationCreate):
    id: int
    created_at: datetime
    created_by: str

    model_config = {"from_attributes": True}


class PumpSessionCreate(BaseModel):
    patient_id: int
    device_configuration_id: int
    clinician_target_map_mmhg: float


class PumpSessionRead(BaseModel):
    id: int
    patient_id: int
    device_configuration_id: int
    clinician_target_map_mmhg: float
    status: str
    started_at: datetime
    ended_at: datetime | None

    model_config = {"from_attributes": True}
