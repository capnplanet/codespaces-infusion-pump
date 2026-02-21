from __future__ import annotations

import json
from pathlib import Path

import pytest

from edge_inference.replay_fixture import stream_fixture


def test_stream_fixture_sends_events(monkeypatch, tmp_path: Path) -> None:
    fixture_path = tmp_path / "telemetry.jsonl"
    fixture_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "session_id": "s-1",
                        "device_id": "pump-01",
                        "sequence": 1,
                        "vitals": [{"name": "map", "value": 64.0, "timestamp_ms": 1000}],
                        "pump_status": {
                            "rate_mcg_per_kg_min": 0.07,
                            "fallback_active": False,
                            "alarm_triggered": False,
                        },
                        "predictions": {"confidence": 0.8},
                    }
                ),
                json.dumps(
                    {
                        "session_id": "s-1",
                        "device_id": "pump-01",
                        "sequence": 2,
                        "vitals": [{"name": "map", "value": 63.0, "timestamp_ms": 2000}],
                        "pump_status": {
                            "rate_mcg_per_kg_min": 0.08,
                            "fallback_active": False,
                            "alarm_triggered": False,
                        },
                        "predictions": {"confidence": 0.81},
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )

    captured = {}

    class FakeAck:
        accepted = True

    class FakeChannel:
        def close(self) -> None:
            captured["closed"] = True

    class FakeStub:
        def StreamTelemetry(self, iterator, metadata, timeout):
            captured["events"] = list(iterator)
            captured["metadata"] = metadata
            captured["timeout"] = timeout
            return FakeAck()

    monkeypatch.setattr("edge_inference.replay_fixture.grpc.insecure_channel", lambda _: FakeChannel())
    monkeypatch.setattr("edge_inference.replay_fixture.telemetry_pb2_grpc.TelemetryIngestionStub", lambda _: FakeStub())

    accepted = stream_fixture(fixture_path=fixture_path, target="localhost:50051", api_key="demo-key")

    assert accepted is True
    assert len(captured["events"]) == 2
    assert captured["events"][0].device_id == "pump-01"
    assert captured["metadata"] == (("x-api-key", "demo-key"), ("x-device-id", "pump-01"))
    assert captured["closed"] is True


def test_stream_fixture_omits_device_header_for_multi_device(monkeypatch, tmp_path: Path) -> None:
    fixture_path = tmp_path / "telemetry-multi.jsonl"
    fixture_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "session_id": "s-1",
                        "device_id": "pump-01",
                        "sequence": 1,
                        "vitals": [{"name": "map", "value": 64.0, "timestamp_ms": 1000}],
                        "pump_status": {
                            "rate_mcg_per_kg_min": 0.07,
                            "fallback_active": False,
                            "alarm_triggered": False,
                        },
                        "predictions": {"confidence": 0.8},
                    }
                ),
                json.dumps(
                    {
                        "session_id": "s-2",
                        "device_id": "pump-02",
                        "sequence": 1,
                        "vitals": [{"name": "map", "value": 65.0, "timestamp_ms": 1000}],
                        "pump_status": {
                            "rate_mcg_per_kg_min": 0.07,
                            "fallback_active": False,
                            "alarm_triggered": False,
                        },
                        "predictions": {"confidence": 0.8},
                    }
                ),
            ]
        ),
        encoding="utf-8",
    )

    captured = {}

    class FakeAck:
        accepted = True

    class FakeChannel:
        def close(self) -> None:
            captured["closed"] = True

    class FakeStub:
        def StreamTelemetry(self, iterator, metadata, timeout):
            captured["events"] = list(iterator)
            captured["metadata"] = metadata
            captured["timeout"] = timeout
            return FakeAck()

    monkeypatch.setattr("edge_inference.replay_fixture.grpc.insecure_channel", lambda _: FakeChannel())
    monkeypatch.setattr("edge_inference.replay_fixture.telemetry_pb2_grpc.TelemetryIngestionStub", lambda _: FakeStub())

    accepted = stream_fixture(fixture_path=fixture_path, target="localhost:50051", api_key="demo-key")

    assert accepted is True
    assert len(captured["events"]) == 2
    assert captured["metadata"] == (("x-api-key", "demo-key"),)
    assert captured["closed"] is True


def test_stream_fixture_tls_channel(monkeypatch, tmp_path: Path) -> None:
    fixture_path = tmp_path / "telemetry.jsonl"
    fixture_path.write_text(
        json.dumps(
            {
                "session_id": "s-1",
                "device_id": "pump-01",
                "sequence": 1,
                "vitals": [{"name": "map", "value": 64.0, "timestamp_ms": 1000}],
                "pump_status": {
                    "rate_mcg_per_kg_min": 0.07,
                    "fallback_active": False,
                    "alarm_triggered": False,
                },
                "predictions": {"confidence": 0.8},
            }
        ),
        encoding="utf-8",
    )

    ca_path = tmp_path / "ca.crt"
    cert_path = tmp_path / "client.crt"
    key_path = tmp_path / "client.key"
    ca_path.write_bytes(b"ca")
    cert_path.write_bytes(b"cert")
    key_path.write_bytes(b"key")

    captured = {}

    class FakeAck:
        accepted = True

    class FakeChannel:
        def close(self) -> None:
            captured["closed"] = True

    class FakeStub:
        def StreamTelemetry(self, iterator, metadata, timeout):
            captured["events"] = list(iterator)
            captured["metadata"] = metadata
            captured["timeout"] = timeout
            return FakeAck()

    def fake_ssl_channel_credentials(root_certificates, private_key, certificate_chain):
        captured["root_certificates"] = root_certificates
        captured["private_key"] = private_key
        captured["certificate_chain"] = certificate_chain
        return "creds"

    def fake_secure_channel(target, credentials):
        captured["target"] = target
        captured["credentials"] = credentials
        return FakeChannel()

    monkeypatch.setattr("edge_inference.replay_fixture.grpc.ssl_channel_credentials", fake_ssl_channel_credentials)
    monkeypatch.setattr("edge_inference.replay_fixture.grpc.secure_channel", fake_secure_channel)
    monkeypatch.setattr("edge_inference.replay_fixture.telemetry_pb2_grpc.TelemetryIngestionStub", lambda _: FakeStub())

    accepted = stream_fixture(
        fixture_path=fixture_path,
        target="ingestion:50051",
        api_key="demo-key",
        tls_enabled=True,
        tls_ca_cert=ca_path,
        tls_client_cert=cert_path,
        tls_client_key=key_path,
    )

    assert accepted is True
    assert captured["target"] == "ingestion:50051"
    assert captured["credentials"] == "creds"
    assert captured["root_certificates"] == b"ca"
    assert captured["certificate_chain"] == b"cert"
    assert captured["private_key"] == b"key"
    assert captured["closed"] is True


def test_stream_fixture_tls_requires_ca(tmp_path: Path) -> None:
    fixture_path = tmp_path / "telemetry.jsonl"
    fixture_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="--tls-ca-cert"):
        stream_fixture(
            fixture_path=fixture_path,
            target="ingestion:50051",
            api_key="demo-key",
            tls_enabled=True,
        )
