"""Telemetry publisher sending predictions to backend."""

from __future__ import annotations

from itertools import count
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
        api_key: str,
        default_session_id: str,
        default_device_id: str,
    ) -> None:
        self._transport = transport.lower()
        self._endpoint = endpoint.rstrip("/")
        self._grpc_target = grpc_target
        self._api_key = api_key
        self._default_session_id = default_session_id
        self._default_device_id = default_device_id
        self._sequence = count(start=1)

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

        channel = grpc.insecure_channel(self._grpc_target)
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
