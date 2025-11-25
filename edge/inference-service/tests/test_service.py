import numpy as np
import pytest
import respx
from fastapi.testclient import TestClient

from edge_inference.config import Settings
from edge_inference.service import app, get_model_runner, get_settings, get_telemetry_client


class StubRunner:
    def run(self, features):
        return np.array([[0.7, 0.8]]), {"inference_ms": 12.0}


class StubTelemetry:
    def __init__(self):
        self.called = False

    def publish_prediction(self, prediction, metadata):
        self.called = True


@pytest.fixture(autouse=True)
def override_dependencies(monkeypatch):
    monkeypatch.setenv("EDGE_INFER_MODEL_PATH", "dummy")

    def _settings():
        return Settings(model_path="dummy")

    monkeypatch.setattr("edge_inference.service.get_settings", _settings)
    monkeypatch.setattr("edge_inference.service.get_model_runner", lambda: StubRunner())
    telemetry = StubTelemetry()
    monkeypatch.setattr("edge_inference.service.get_telemetry_client", lambda: telemetry)
    return telemetry


def test_predict_success(override_dependencies):
    client = TestClient(app)
    response = client.post("/predict", json={"features": {"x": [1.0]}})
    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] == pytest.approx(0.8)


def test_predict_low_confidence(monkeypatch):
    client = TestClient(app)

    class LowConfidenceRunner:
        def run(self, features):
            return np.array([[0.1, 0.2]]), {"inference_ms": 5.0}

    monkeypatch.setattr("edge_inference.service.get_model_runner", lambda: LowConfidenceRunner())
    response = client.post("/predict", json={"features": {"x": [1.0]}})
    assert response.status_code == 409
