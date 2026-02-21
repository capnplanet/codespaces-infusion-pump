from __future__ import annotations

from pathlib import Path

import pytest

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


def test_publish_prediction_grpc_transport_with_tls(monkeypatch, tmp_path: Path) -> None:
    captured = {}

    ca_path = tmp_path / "ca.crt"
    cert_path = tmp_path / "client.crt"
    key_path = tmp_path / "client.key"
    ca_path.write_bytes(b"ca")
    cert_path.write_bytes(b"cert")
    key_path.write_bytes(b"key")

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

    def fake_ssl_channel_credentials(root_certificates, private_key, certificate_chain):
        captured["root_certificates"] = root_certificates
        captured["private_key"] = private_key
        captured["certificate_chain"] = certificate_chain
        return "fake-creds"

    def fake_secure_channel(target, credentials):
        captured["target"] = target
        captured["credentials"] = credentials
        return FakeChannel()

    monkeypatch.setattr("edge_inference.telemetry_client.grpc.ssl_channel_credentials", fake_ssl_channel_credentials)
    monkeypatch.setattr("edge_inference.telemetry_client.grpc.secure_channel", fake_secure_channel)
    monkeypatch.setattr("edge_inference.telemetry_client.telemetry_pb2_grpc.TelemetryIngestionStub", lambda channel: FakeStub())

    client = TelemetryClient(
        transport="grpc",
        endpoint="http://unused",
        grpc_target="ingestion:50051",
        grpc_use_tls=True,
        grpc_tls_ca_cert=ca_path,
        grpc_tls_client_cert=cert_path,
        grpc_tls_client_key=key_path,
        api_key="device-key",
        default_session_id="demo-session",
        default_device_id="pump-07",
    )

    client.publish_prediction([64.2], {"confidence": 0.86})

    assert captured["target"] == "ingestion:50051"
    assert captured["credentials"] == "fake-creds"
    assert captured["root_certificates"] == b"ca"
    assert captured["certificate_chain"] == b"cert"
    assert captured["private_key"] == b"key"
    assert captured["closed"] is True


def test_publish_prediction_grpc_tls_requires_ca() -> None:
    client = TelemetryClient(
        transport="grpc",
        endpoint="http://unused",
        grpc_target="ingestion:50051",
        grpc_use_tls=True,
        api_key="device-key",
        default_session_id="demo-session",
        default_device_id="pump-07",
    )

    with pytest.raises(RuntimeError, match="no CA certificate"):
        client.publish_prediction([64.2], {"confidence": 0.86})
