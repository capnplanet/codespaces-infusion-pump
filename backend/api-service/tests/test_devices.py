from __future__ import annotations

from fastapi.testclient import TestClient


def test_device_configuration_flow(client: TestClient) -> None:
    payload = {
        "device_id": "pump-001",
        "firmware_version": "1.0.0",
        "gateway_version": "0.1.0",
        "config_payload": {"max_rate": 0.8},
    }
    response = client.post("/devices/configurations", json=payload)
    assert response.status_code == 201
    config = response.json()
    assert config["device_id"] == "pump-001"

    response = client.get(f"/devices/configurations/{config['id']}")
    assert response.status_code == 200
    fetched = response.json()
    assert fetched["device_id"] == "pump-001"
