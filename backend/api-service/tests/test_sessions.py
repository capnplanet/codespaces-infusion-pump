from __future__ import annotations

from fastapi.testclient import TestClient


def create_patient(client: TestClient) -> int:
    response = client.post(
        "/patients/",
        json={"mrn": "abc", "demographics": {"age": 60}},
    )
    return response.json()["id"]


def create_config(client: TestClient) -> int:
    response = client.post(
        "/devices/configurations",
        json={
            "device_id": "pump-002",
            "firmware_version": "1.0.0",
            "gateway_version": "0.1.0",
            "config_payload": {"max_rate": 0.7},
        },
    )
    return response.json()["id"]


def test_session_lifecycle(client: TestClient) -> None:
    patient_id = create_patient(client)
    config_id = create_config(client)

    response = client.post(
        "/sessions/",
        json={
            "patient_id": patient_id,
            "device_configuration_id": config_id,
            "clinician_target_map_mmhg": 65.0,
        },
    )
    assert response.status_code == 201
    session = response.json()
    assert session["status"] == "active"

    response = client.post(f"/sessions/{session['id']}/close")
    assert response.status_code == 200
    closed = response.json()
    assert closed["status"] == "closed"
    assert closed["ended_at"] is not None
