"""Placeholder protobuf definitions for development stubs.

In production this file is generated from `proto/telemetry.proto` using
`grpc_tools.protoc`. The placeholder keeps the repository runnable for linting
and unit tests without requiring code generation at authoring time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TelemetryEnvelope:
    session_id: str
    device_id: str
    vitals: List[dict] = field(default_factory=list)
    pump_status: dict | None = None
    predictions: Dict[str, float] = field(default_factory=dict)
    sequence: int = 0

    def SerializeToString(self) -> bytes:
        # Placeholder implementation; replace with protobuf serialization.
        return repr(self.__dict__).encode()


@dataclass
class TelemetryAck:
    accepted: bool
