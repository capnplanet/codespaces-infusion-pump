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


def _build_grpc_channel(
    *,
    target: str,
    use_tls: bool,
    tls_ca_cert: Path | None,
    tls_client_cert: Path | None,
    tls_client_key: Path | None,
):
    if not use_tls:
        return grpc.insecure_channel(target)

    if tls_ca_cert is None:
        raise ValueError("TLS is enabled but --tls-ca-cert was not provided")
    if (tls_client_cert is None) != (tls_client_key is None):
        raise ValueError("mTLS requires both --tls-client-cert and --tls-client-key")

    root_certificates = tls_ca_cert.read_bytes()
    certificate_chain = tls_client_cert.read_bytes() if tls_client_cert else None
    private_key = tls_client_key.read_bytes() if tls_client_key else None
    credentials = grpc.ssl_channel_credentials(
        root_certificates=root_certificates,
        private_key=private_key,
        certificate_chain=certificate_chain,
    )
    return grpc.secure_channel(target, credentials)


def stream_fixture(
    *,
    fixture_path: Path,
    target: str,
    api_key: str,
    tls_enabled: bool = False,
    tls_ca_cert: Path | None = None,
    tls_client_cert: Path | None = None,
    tls_client_key: Path | None = None,
) -> bool:
    channel = _build_grpc_channel(
        target=target,
        use_tls=tls_enabled,
        tls_ca_cert=tls_ca_cert,
        tls_client_cert=tls_client_cert,
        tls_client_key=tls_client_key,
    )
    try:
        stub = telemetry_pb2_grpc.TelemetryIngestionStub(channel)
        events = list(_iter_fixture_events(fixture_path))

        unique_device_ids = {event.device_id for event in events}
        single_device_id = next(iter(unique_device_ids)) if len(unique_device_ids) == 1 else None

        metadata = (("x-api-key", api_key),)
        if single_device_id:
            metadata = (("x-api-key", api_key), ("x-device-id", single_device_id))

        ack = stub.StreamTelemetry(iter(events), metadata=metadata, timeout=5.0)
        return bool(ack.accepted)
    finally:
        channel.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--target", type=str, default="localhost:50051")
    parser.add_argument("--api-key", type=str, required=True)
    parser.add_argument("--tls-enabled", action="store_true")
    parser.add_argument("--tls-ca-cert", type=Path)
    parser.add_argument("--tls-client-cert", type=Path)
    parser.add_argument("--tls-client-key", type=Path)
    args = parser.parse_args()

    tls_enabled = bool(
        args.tls_enabled
        or args.tls_ca_cert is not None
        or args.tls_client_cert is not None
        or args.tls_client_key is not None
    )

    accepted = stream_fixture(
        fixture_path=args.fixture,
        target=args.target,
        api_key=args.api_key,
        tls_enabled=tls_enabled,
        tls_ca_cert=args.tls_ca_cert,
        tls_client_cert=args.tls_client_cert,
        tls_client_key=args.tls_client_key,
    )
    if not accepted:
        raise SystemExit("ingestion did not accept fixture stream")
    print(f"streamed fixture to {args.target}: {args.fixture}")


if __name__ == "__main__":
    main()
