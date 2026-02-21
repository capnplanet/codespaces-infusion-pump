"""Patient management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import hash_identifier, require_roles
from ..core.settings import APISettings, get_settings
from ..models import domain
from ..schemas import patient as patient_schema

router = APIRouter()


@router.post("/", response_model=patient_schema.PatientRead, status_code=status.HTTP_201_CREATED)
async def create_patient(
    payload: patient_schema.PatientCreate,
    db: AsyncSession = Depends(get_db),
    settings: APISettings = Depends(get_settings),
    user: dict = Depends(require_roles("admin", "clinician")),
) -> patient_schema.PatientRead:
    stmt = select(domain.Patient).where(domain.Patient.mrn == payload.mrn)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Patient already exists")

    patient = domain.Patient(
        mrn=payload.mrn,
        hashed_mrn=hash_identifier(payload.mrn, settings.mrn_hash_salt),
        demographics=payload.demographics,
        created_by=user["sub"],
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=patient_schema.PatientRead)
async def get_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles("admin", "clinician", "auditor")),
) -> patient_schema.PatientRead:
    patient = await db.get(domain.Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient
