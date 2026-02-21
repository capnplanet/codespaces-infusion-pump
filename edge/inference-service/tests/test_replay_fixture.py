from __future__ import annotations

import json
from pathlib import Path

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
