from __future__ import annotations

from edge_inference.telemetry_client import TelemetryClient


def test_publish_prediction_http_transport(monkeypatch) -> None:
    calls = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

    def fake_post(url, json, headers, timeout):
        calls["url"] = url
        calls["json"] = json
        calls["headers"] = headers
        calls["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("edge_inference.telemetry_client.httpx.post", fake_post)

    client = TelemetryClient(
        transport="http",
        endpoint="http://localhost:8081/telemetry",
        grpc_target="localhost:50051",
        api_key="token",
        default_session_id="demo-session",
        default_device_id="pump-01",
    )

    client.publish_prediction([67.0], {"confidence": 0.8, "inference_ms": 10.0})

    assert calls["url"] == "http://localhost:8081/telemetry"
    assert calls["json"]["prediction"] == [67.0]
    assert calls["headers"]["Authorization"] == "Bearer token"


def test_publish_prediction_grpc_transport(monkeypatch) -> None:
    captured = {}

    class FakeAck:
        accepted = True

    class FakeChannel:
        def close(self) -> None:
            captured["closed"] = True

    class FakeStub:
        def StreamTelemetry(self, iterator, metadata, timeout):
            events = list(iterator)
            captured["event"] = events[0]
            captured["metadata"] = metadata
            captured["timeout"] = timeout
            return FakeAck()

    monkeypatch.setattr("edge_inference.telemetry_client.grpc.insecure_channel", lambda target: FakeChannel())
    monkeypatch.setattr("edge_inference.telemetry_client.telemetry_pb2_grpc.TelemetryIngestionStub", lambda channel: FakeStub())

    client = TelemetryClient(
        transport="grpc",
        endpoint="http://unused",
        grpc_target="localhost:50051",
        api_key="device-key",
        default_session_id="demo-session",
        default_device_id="pump-07",
    )

    client.publish_prediction(
        [64.2],
        {
            "confidence": 0.86,
            "inference_ms": 7.0,
            "fallback_active": False,
            "alarm_triggered": False,
        },
    )

    event = captured["event"]
    assert event.session_id == "demo-session"
    assert event.device_id == "pump-07"
    assert event.predictions["confidence"] == 0.86
    assert captured["metadata"] == (("x-api-key", "device-key"), ("x-device-id", "pump-07"))
    assert captured["closed"] is True
