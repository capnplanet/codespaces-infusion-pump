"""Replay telemetry fixture JSONL streams into ingestion gRPC service."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import grpc

from .ingestion_proto import telemetry_pb2, telemetry_pb2_grpc


def _event_to_envelope(event: dict) -> telemetry_pb2.TelemetryEnvelope:
    vitals = [
        telemetry_pb2.VitalReading(
            name=str(vital.get("name", "")),
            value=float(vital.get("value", 0.0)),
            timestamp_ms=int(vital.get("timestamp_ms", 0)),
        )
        for vital in event.get("vitals", [])
    ]
    pump_status = event.get("pump_status", {})
    predictions = {str(k): float(v) for k, v in event.get("predictions", {}).items()}

    return telemetry_pb2.TelemetryEnvelope(
        session_id=str(event["session_id"]),
        device_id=str(event["device_id"]),
        sequence=int(event["sequence"]),
        vitals=vitals,
        pump_status=telemetry_pb2.PumpStatus(
            rate_mcg_per_kg_min=float(pump_status.get("rate_mcg_per_kg_min", 0.0)),
            fallback_active=bool(pump_status.get("fallback_active", False)),
            alarm_triggered=bool(pump_status.get("alarm_triggered", False)),
        ),
        predictions=predictions,
    )


def _iter_fixture_events(fixture_path: Path):
    with fixture_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                event = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}") from exc
            yield _event_to_envelope(event)


def stream_fixture(*, fixture_path: Path, target: str, api_key: str) -> bool:
    channel = grpc.insecure_channel(target)
    try:
        stub = telemetry_pb2_grpc.TelemetryIngestionStub(channel)
        first_device_id = None
        events = list(_iter_fixture_events(fixture_path))
        if events:
            first_device_id = events[0].device_id

        metadata = (("x-api-key", api_key),)
        if first_device_id:
            metadata = (("x-api-key", api_key), ("x-device-id", first_device_id))

        ack = stub.StreamTelemetry(iter(events), metadata=metadata, timeout=5.0)
        return bool(ack.accepted)
    finally:
        channel.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--target", type=str, default="localhost:50051")
    parser.add_argument("--api-key", type=str, required=True)
    args = parser.parse_args()

    accepted = stream_fixture(fixture_path=args.fixture, target=args.target, api_key=args.api_key)
    if not accepted:
        raise SystemExit("ingestion did not accept fixture stream")
    print(f"streamed fixture to {args.target}: {args.fixture}")


if __name__ == "__main__":
    main()
