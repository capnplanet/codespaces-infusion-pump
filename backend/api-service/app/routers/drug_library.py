"""Drug library management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import require_roles
from ..models import domain
from ..schemas import drug_library as drug_schema

router = APIRouter()


@router.post("/", response_model=drug_schema.DrugLibraryEntryRead, status_code=status.HTTP_201_CREATED)
async def create_entry(
    payload: drug_schema.DrugLibraryEntryCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles("admin")),
) -> drug_schema.DrugLibraryEntryRead:
    stmt = select(domain.DrugLibraryEntry).where(domain.DrugLibraryEntry.drug_name == payload.drug_name)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Drug already exists")

    entry = domain.DrugLibraryEntry(
        drug_name=payload.drug_name,
        concentration_mcg_per_ml=payload.concentration_mcg_per_ml,
        min_rate_mcg_per_kg_min=payload.min_rate_mcg_per_kg_min,
        max_rate_mcg_per_kg_min=payload.max_rate_mcg_per_kg_min,
        max_delta_mcg_per_kg_min=payload.max_delta_mcg_per_kg_min,
        safety_notes=payload.safety_notes,
        created_by=user["sub"],
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.get("/{entry_id}", response_model=drug_schema.DrugLibraryEntryRead)
async def get_entry(
    entry_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles("admin", "clinician", "auditor")),
) -> drug_schema.DrugLibraryEntryRead:
    entry = await db.get(domain.DrugLibraryEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return entry
