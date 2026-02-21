from __future__ import annotations

import numpy as np
from fastapi.testclient import TestClient

from edge_inference.config import Settings
from edge_inference.service import app, get_model_runner, get_settings, get_telemetry_client


class StubRunner:
    def __init__(self, prediction: np.ndarray, metadata: dict):
        self._prediction = prediction
        self._metadata = metadata

    def run(self, features):
        return self._prediction, self._metadata


class StubTelemetry:
    def __init__(self):
        self.calls = []

    def publish_prediction(self, prediction, metadata):
        self.calls.append({"prediction": prediction, "metadata": metadata})


def test_predict_success_with_explicit_confidence() -> None:
    runner = StubRunner(np.array([[0.7, 0.8]]), {"inference_ms": 12.0, "confidence": 0.83})
    telemetry = StubTelemetry()

    app.dependency_overrides[get_settings] = lambda: Settings(model_path="dummy")
    app.dependency_overrides[get_model_runner] = lambda: runner
    app.dependency_overrides[get_telemetry_client] = lambda: telemetry

    client = TestClient(app)
    response = client.post("/predict", json={"features": {"x": [1.0]}})

    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] == 0.83
    assert data["map_forecast"] == [0.7, 0.8]
    assert len(telemetry.calls) == 1

    app.dependency_overrides.clear()


def test_predict_low_confidence() -> None:
    runner = StubRunner(np.array([[0.1, 0.2]]), {"inference_ms": 5.0, "confidence": 0.2})

    app.dependency_overrides[get_settings] = lambda: Settings(model_path="dummy", min_confidence=0.5)
    app.dependency_overrides[get_model_runner] = lambda: runner
    app.dependency_overrides[get_telemetry_client] = lambda: StubTelemetry()

    client = TestClient(app)
    response = client.post("/predict", json={"features": {"x": [1.0]}})

    assert response.status_code == 409
    app.dependency_overrides.clear()


def test_predict_rejects_feature_contract_mismatch() -> None:
    runner = StubRunner(np.array([[0.7, 0.8]]), {"inference_ms": 5.0, "confidence": 0.8})

    app.dependency_overrides[get_settings] = lambda: Settings(
        model_path="dummy",
        required_feature_names=["hr", "map"],
    )
    app.dependency_overrides[get_model_runner] = lambda: runner
    app.dependency_overrides[get_telemetry_client] = lambda: StubTelemetry()

    client = TestClient(app)
    response = client.post("/predict", json={"features": {"hr": [80.0]}})

    assert response.status_code == 422
    app.dependency_overrides.clear()


def test_predict_rejects_missing_confidence_when_legacy_disabled() -> None:
    runner = StubRunner(np.array([[0.7, 0.8]]), {"inference_ms": 5.0})

    app.dependency_overrides[get_settings] = lambda: Settings(
        model_path="dummy",
        allow_legacy_confidence_index=False,
    )
    app.dependency_overrides[get_model_runner] = lambda: runner
    app.dependency_overrides[get_telemetry_client] = lambda: StubTelemetry()

    client = TestClient(app)
    response = client.post("/predict", json={"features": {"x": [1.0]}})

    assert response.status_code == 502
    app.dependency_overrides.clear()


def test_predict_rejects_out_of_range_confidence() -> None:
    runner = StubRunner(np.array([[0.7, 0.8]]), {"inference_ms": 5.0, "confidence": 1.5})

    app.dependency_overrides[get_settings] = lambda: Settings(model_path="dummy")
    app.dependency_overrides[get_model_runner] = lambda: runner
    app.dependency_overrides[get_telemetry_client] = lambda: StubTelemetry()

    client = TestClient(app)
    response = client.post("/predict", json={"features": {"x": [1.0]}})

    assert response.status_code == 502
    app.dependency_overrides.clear()
