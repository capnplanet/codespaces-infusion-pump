from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_identifier
from app.models.domain import Patient


def test_hash_identifier_is_deterministic() -> None:
    mrn = "12345"
    assert hash_identifier(mrn, "test-salt") == hash_identifier(mrn, "test-salt")
    assert hash_identifier(mrn, "test-salt") != hash_identifier(mrn, "different-salt")


@pytest.mark.asyncio
async def test_patient_record_stores_hashed_mrn(client, db_session: AsyncSession) -> None:
    payload = {
        "mrn": "patient-001",
        "demographics": {"age": 65, "weight_kg": 80},
    }
    response = client.post("/patients/", json=payload)
    assert response.status_code == 201
    created_id = response.json()["id"]

    stmt = select(Patient).where(Patient.id == created_id)
    patient = (await db_session.execute(stmt)).scalar_one()

    assert patient.hashed_mrn != payload["mrn"]
    assert patient.hashed_mrn == hash_identifier(payload["mrn"], "test-salt")
