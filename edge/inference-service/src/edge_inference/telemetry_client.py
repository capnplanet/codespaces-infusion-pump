"""Telemetry publisher sending predictions to backend."""

from __future__ import annotations

from itertools import count
from pathlib import Path
from typing import Any, Dict, List

import grpc
import httpx

from .ingestion_proto import telemetry_pb2, telemetry_pb2_grpc


class TelemetryClient:
    """Telemetry client supporting HTTP and gRPC ingestion contracts."""

    def __init__(
        self,
        *,
        transport: str,
        endpoint: str,
        grpc_target: str,
        grpc_use_tls: bool = False,
        grpc_tls_ca_cert: Path | None = None,
        grpc_tls_client_cert: Path | None = None,
        grpc_tls_client_key: Path | None = None,
        api_key: str,
        default_session_id: str,
        default_device_id: str,
    ) -> None:
        self._transport = transport.lower()
        self._endpoint = endpoint.rstrip("/")
        self._grpc_target = grpc_target
        self._grpc_use_tls = grpc_use_tls
        self._grpc_tls_ca_cert = grpc_tls_ca_cert
        self._grpc_tls_client_cert = grpc_tls_client_cert
        self._grpc_tls_client_key = grpc_tls_client_key
        self._api_key = api_key
        self._default_session_id = default_session_id
        self._default_device_id = default_device_id
        self._sequence = count(start=1)

    def _grpc_channel(self):
        if not self._grpc_use_tls:
            return grpc.insecure_channel(self._grpc_target)

        if self._grpc_tls_ca_cert is None:
            raise RuntimeError("gRPC TLS is enabled but no CA certificate path was configured")

        if (self._grpc_tls_client_cert is None) != (self._grpc_tls_client_key is None):
            raise RuntimeError("gRPC mTLS requires both client cert and client key")

        root_certificates = self._grpc_tls_ca_cert.read_bytes()
        certificate_chain = None
        private_key = None
        if self._grpc_tls_client_cert is not None and self._grpc_tls_client_key is not None:
            certificate_chain = self._grpc_tls_client_cert.read_bytes()
            private_key = self._grpc_tls_client_key.read_bytes()

        credentials = grpc.ssl_channel_credentials(
            root_certificates=root_certificates,
            private_key=private_key,
            certificate_chain=certificate_chain,
        )
        return grpc.secure_channel(self._grpc_target, credentials)

    def publish_prediction(self, prediction: List[float], metadata: Dict[str, Any]) -> None:
        if self._transport == "grpc":
            self._publish_prediction_grpc(prediction=prediction, metadata=metadata)
            return
        self._publish_prediction_http(prediction=prediction, metadata=metadata)

    def _publish_prediction_http(self, prediction: List[float], metadata: Dict[str, Any]) -> None:
        payload = {"prediction": prediction, "metadata": metadata}
        headers = {"Authorization": f"Bearer {self._api_key}"}
        response = httpx.post(f"{self._endpoint}", json=payload, headers=headers, timeout=1.0)
        response.raise_for_status()

    def _publish_prediction_grpc(self, prediction: List[float], metadata: Dict[str, Any]) -> None:
        session_id = str(metadata.get("session_id", self._default_session_id))
        device_id = str(metadata.get("device_id", self._default_device_id))
        map_value = float(metadata.get("map", prediction[0] if prediction else 0.0))
        confidence = float(metadata.get("confidence", 0.0))

        envelope = telemetry_pb2.TelemetryEnvelope(
            session_id=session_id,
            device_id=device_id,
            sequence=int(metadata.get("sequence", next(self._sequence))),
            vitals=[
                telemetry_pb2.VitalReading(name="map", value=map_value, timestamp_ms=0),
            ],
            pump_status=telemetry_pb2.PumpStatus(
                rate_mcg_per_kg_min=float(metadata.get("rate_mcg_per_kg_min", 0.0)),
                fallback_active=bool(metadata.get("fallback_active", False)),
                alarm_triggered=bool(metadata.get("alarm_triggered", False)),
            ),
            predictions={
                "confidence": confidence,
                "map_forecast": float(prediction[0] if prediction else 0.0),
            },
        )

        channel = self._grpc_channel()
        try:
            stub = telemetry_pb2_grpc.TelemetryIngestionStub(channel)
            ack = stub.StreamTelemetry(
                iter([envelope]),
                metadata=(("x-api-key", self._api_key), ("x-device-id", device_id)),
                timeout=1.0,
            )
            if not ack.accepted:
                raise RuntimeError("ingestion rejected telemetry envelope")
        finally:
            channel.close()
