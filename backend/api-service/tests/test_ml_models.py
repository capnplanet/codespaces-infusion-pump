from __future__ import annotations

from fastapi.testclient import TestClient


def test_register_model_version(client: TestClient) -> None:
    payload = {
        "registry_id": "map-predictor",
        "version": "1.0.0",
        "dataset_hash": "abc123",
        "validation_report_path": "s3://reports/map-v1.json",
        "acceptance_summary": {"auroc": 0.9},
    }
    response = client.post("/ml-models/", json=payload)
    assert response.status_code == 201
    model = response.json()
    assert model["registry_id"] == "map-predictor"

    response = client.get(f"/ml-models/{model['id']}")
    assert response.status_code == 200
