from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.security import get_current_user
from app.main import app


@pytest.fixture
def as_viewer() -> Generator[None, None, None]:
    app.dependency_overrides[get_current_user] = lambda: {"sub": "viewer-user", "roles": ["viewer"]}
    yield
    app.dependency_overrides[get_current_user] = lambda: {"sub": "tester", "roles": ["admin"]}


@pytest.fixture
def as_clinician() -> Generator[None, None, None]:
    app.dependency_overrides[get_current_user] = lambda: {"sub": "clinician-user", "roles": ["clinician"]}
    yield
    app.dependency_overrides[get_current_user] = lambda: {"sub": "tester", "roles": ["admin"]}


def test_drug_library_create_requires_admin(client: TestClient, as_viewer) -> None:
    response = client.post(
        "/drug-library/",
        json={
            "drug_name": "Norepinephrine",
            "concentration_mcg_per_ml": 64.0,
            "min_rate_mcg_per_kg_min": 0.01,
            "max_rate_mcg_per_kg_min": 3.0,
            "max_delta_mcg_per_kg_min": 0.2,
            "safety_notes": "vasopressor",
        },
    )
    assert response.status_code == 403


def test_device_configuration_create_requires_admin(client: TestClient, as_clinician) -> None:
    response = client.post(
        "/devices/configurations",
        json={
            "device_id": "pump-rbac-1",
            "firmware_version": "1.0.0",
            "gateway_version": "0.1.0",
            "config_payload": {"max_rate": 0.7},
        },
    )
    assert response.status_code == 403


def test_patient_create_allows_clinician(client: TestClient, as_clinician) -> None:
    response = client.post(
        "/patients/",
        json={"mrn": "rbac-clinician-1", "demographics": {"age": 58}},
    )
    assert response.status_code == 201


def test_audit_events_requires_auditor_or_admin(client: TestClient, as_clinician) -> None:
    response = client.get("/audit/events")
    assert response.status_code == 403
