from __future__ import annotations

from fastapi.testclient import TestClient


def test_drug_library_entry(client: TestClient) -> None:
    payload = {
        "drug_name": "norepinephrine",
        "concentration_mcg_per_ml": 64.0,
        "min_rate_mcg_per_kg_min": 0.02,
        "max_rate_mcg_per_kg_min": 1.0,
        "max_delta_mcg_per_kg_min": 0.1,
        "safety_notes": "Monitor MAP closely",
    }
    response = client.post("/drug-library/", json=payload)
    assert response.status_code == 201
    entry = response.json()
    assert entry["drug_name"] == "norepinephrine"

    response = client.get(f"/drug-library/{entry['id']}")
    assert response.status_code == 200
