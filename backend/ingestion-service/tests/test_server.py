from __future__ import annotations

from collections.abc import AsyncIterator

import grpc
import pytest

from ingestion_service import telemetry_pb2
from ingestion_service.server import TelemetryIngestionService


class FakeProducer:
    def __init__(self, fail_times: int = 0) -> None:
        self.fail_times = fail_times
        self.attempts = 0
        self.sent: list[tuple[str, bytes, bytes]] = []

    async def send_and_wait(self, topic: str, payload: bytes, key: bytes) -> None:
        self.attempts += 1
        if self.attempts <= self.fail_times:
            raise RuntimeError("transient kafka failure")
        self.sent.append((topic, payload, key))


class FakeContext:
    def __init__(self) -> None:
        self.aborted = False
        self.abort_status = None
        self.abort_message = None

    async def abort(self, status_code, details) -> None:
        self.aborted = True
        self.abort_status = status_code
        self.abort_message = details
        raise RuntimeError("aborted")


async def stream_from(items: list[telemetry_pb2.TelemetryEnvelope]) -> AsyncIterator[telemetry_pb2.TelemetryEnvelope]:
    for item in items:
        yield item


@pytest.mark.asyncio
async def test_stream_retries_then_succeeds() -> None:
    producer = FakeProducer(fail_times=2)
    sleeps: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    service = TelemetryIngestionService(
        producer,
        "telemetry.events",
        max_retries=3,
        backoff_initial_seconds=0.1,
        backoff_max_seconds=1.0,
        idempotency_cache_size=100,
        sleep_func=fake_sleep,
    )

    envelope = telemetry_pb2.TelemetryEnvelope(session_id="s1", device_id="d1", sequence=1)
    ack = await service.StreamTelemetry(stream_from([envelope]), FakeContext())

    assert ack.accepted is True
    assert producer.attempts == 3
    assert len(producer.sent) == 1
    assert sleeps == [0.1, 0.2]


@pytest.mark.asyncio
async def test_stream_skips_duplicate_sequence() -> None:
    producer = FakeProducer()

    service = TelemetryIngestionService(
        producer,
        "telemetry.events",
        max_retries=1,
        backoff_initial_seconds=0.1,
        backoff_max_seconds=1.0,
        idempotency_cache_size=100,
    )

    first = telemetry_pb2.TelemetryEnvelope(session_id="s1", device_id="d1", sequence=7)
    duplicate = telemetry_pb2.TelemetryEnvelope(session_id="s1", device_id="d1", sequence=7)
    older = telemetry_pb2.TelemetryEnvelope(session_id="s1", device_id="d1", sequence=6)
    newer = telemetry_pb2.TelemetryEnvelope(session_id="s1", device_id="d1", sequence=8)

    ack = await service.StreamTelemetry(stream_from([first, duplicate, older, newer]), FakeContext())

    assert ack.accepted is True
    assert producer.attempts == 2
    assert len(producer.sent) == 2


@pytest.mark.asyncio
async def test_stream_aborts_after_retry_exhaustion() -> None:
    producer = FakeProducer(fail_times=10)
    context = FakeContext()

    service = TelemetryIngestionService(
        producer,
        "telemetry.events",
        max_retries=2,
        backoff_initial_seconds=0.01,
        backoff_max_seconds=0.02,
        idempotency_cache_size=100,
    )

    envelope = telemetry_pb2.TelemetryEnvelope(session_id="s1", device_id="d1", sequence=1)

    with pytest.raises(RuntimeError, match="aborted"):
        await service.StreamTelemetry(stream_from([envelope]), context)

    assert context.aborted is True
    assert context.abort_status == grpc.StatusCode.INTERNAL
    assert context.abort_message == "Failed to publish telemetry"
    assert producer.attempts == 3
    assert len(producer.sent) == 0
