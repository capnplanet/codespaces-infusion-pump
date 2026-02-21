"""ML model registry endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import require_roles
from ..models import domain
from ..schemas import ml as ml_schema

router = APIRouter()


@router.post("/", response_model=ml_schema.ModelVersionRead, status_code=status.HTTP_201_CREATED)
async def register_model(
    payload: ml_schema.ModelVersionCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles("admin")),
) -> ml_schema.ModelVersionRead:
    stmt = select(domain.MLModelVersion).where(domain.MLModelVersion.registry_id == payload.registry_id)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        if existing.version == payload.version:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Model version already registered")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Registry ID already exists; choose a new registry_id",
        )

    model = domain.MLModelVersion(
        registry_id=payload.registry_id,
        version=payload.version,
        dataset_hash=payload.dataset_hash,
        validation_report_path=payload.validation_report_path,
        acceptance_summary=payload.acceptance_summary,
        created_by=user["sub"],
    )
    db.add(model)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Model version already registered or registry_id already exists",
        ) from exc
    await db.refresh(model)
    return model


@router.get("/{model_id}", response_model=ml_schema.ModelVersionRead)
async def get_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_roles("admin", "clinician", "auditor")),
) -> ml_schema.ModelVersionRead:
    model = await db.get(domain.MLModelVersion, model_id)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    return model
