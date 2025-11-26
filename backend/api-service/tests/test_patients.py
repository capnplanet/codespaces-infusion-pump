from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_and_fetch_patient(client: TestClient) -> None:
    payload = {
        "mrn": "12345",
        "demographics": {"age": 65, "weight_kg": 80},
    }
    response = client.post("/patients/", json=payload)
    assert response.status_code == 201
    patient = response.json()
    assert patient["mrn"] == "12345"

    response = client.get(f"/patients/{patient['id']}")
    assert response.status_code == 200
    fetched = response.json()
    assert fetched["mrn"] == "12345"
