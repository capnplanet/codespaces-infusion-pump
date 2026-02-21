"""gRPC server implementation for telemetry ingestion."""

from __future__ import annotations

import asyncio
from collections import OrderedDict
from collections.abc import Awaitable, Callable

import grpc
from aiokafka import AIOKafkaProducer
from structlog import get_logger

from . import telemetry_pb2, telemetry_pb2_grpc
from .config import get_settings

LOGGER = get_logger()


class TelemetryIngestionService(telemetry_pb2_grpc.TelemetryIngestionServicer):
    """Streams telemetry messages into Kafka topic."""

    def __init__(
        self,
        producer: AIOKafkaProducer,
        topic: str,
        *,
        max_retries: int,
        backoff_initial_seconds: float,
        backoff_max_seconds: float,
        idempotency_cache_size: int,
        sleep_func: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._producer = producer
        self._topic = topic
        self._max_retries = max(0, max_retries)
        self._backoff_initial_seconds = max(0.0, backoff_initial_seconds)
        self._backoff_max_seconds = max(self._backoff_initial_seconds, backoff_max_seconds)
        self._idempotency_cache_size = max(1, idempotency_cache_size)
        self._sleep = sleep_func
        self._last_seen_sequence: OrderedDict[tuple[str, str], int] = OrderedDict()

    def _is_replayed(self, *, session_id: str, device_id: str, sequence: int) -> bool:
        key = (session_id, device_id)
        previous = self._last_seen_sequence.get(key)
        if previous is not None and sequence <= previous:
            self._last_seen_sequence.move_to_end(key)
            return True
        self._last_seen_sequence[key] = sequence
        self._last_seen_sequence.move_to_end(key)
        if len(self._last_seen_sequence) > self._idempotency_cache_size:
            self._last_seen_sequence.popitem(last=False)
        return False

    async def _publish_with_retry(self, *, payload: bytes, key: bytes, metadata: dict) -> None:
        attempt = 0
        backoff = self._backoff_initial_seconds
        while True:
            try:
                await self._producer.send_and_wait(self._topic, payload, key=key)
                return
            except Exception as exc:
                if attempt >= self._max_retries:
                    LOGGER.error("telemetry_publish_failed", attempts=attempt + 1, error=str(exc), **metadata)
                    raise
                LOGGER.warning("telemetry_publish_retry", attempt=attempt + 1, backoff_seconds=backoff, error=str(exc), **metadata)
                await self._sleep(backoff)
                attempt += 1
                backoff = min(self._backoff_max_seconds, backoff * 2 if backoff > 0 else self._backoff_initial_seconds)

    async def StreamTelemetry(self, request_iterator, context):  # type: ignore[override]
        async for envelope in request_iterator:
            if self._is_replayed(
                session_id=envelope.session_id,
                device_id=envelope.device_id,
                sequence=envelope.sequence,
            ):
                LOGGER.info(
                    "telemetry_duplicate_skipped",
                    session_id=envelope.session_id,
                    device_id=envelope.device_id,
                    sequence=envelope.sequence,
                )
                continue

            payload = envelope.SerializeToString()
            metadata = {
                "session_id": envelope.session_id,
                "device_id": envelope.device_id,
                "sequence": envelope.sequence,
            }
            try:
                await self._publish_with_retry(
                    payload=payload,
                    key=envelope.session_id.encode(),
                    metadata=metadata,
                )
            except Exception:
                await context.abort(grpc.StatusCode.INTERNAL, "Failed to publish telemetry")
            LOGGER.info("telemetry_ingested", **metadata)
        return telemetry_pb2.TelemetryAck(accepted=True)


async def serve() -> None:
    settings = get_settings()
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)
    await producer.start()

    server = grpc.aio.server()
    try:
        telemetry_pb2_grpc.add_TelemetryIngestionServicer_to_server(
            TelemetryIngestionService(
                producer,
                settings.kafka_topic,
                max_retries=settings.kafka_send_max_retries,
                backoff_initial_seconds=settings.kafka_send_backoff_initial_seconds,
                backoff_max_seconds=settings.kafka_send_backoff_max_seconds,
                idempotency_cache_size=settings.idempotency_cache_size,
            ),
            server,
        )
    except NotImplementedError:
        LOGGER.warning("grpc_bindings_not_generated")
        await producer.stop()
        return
    with open(settings.tls_key_path, "rb") as key_file, open(settings.tls_cert_path, "rb") as cert_file:
        private_key = key_file.read()
        certificate_chain = cert_file.read()
    with open(settings.tls_ca_path, "rb") as ca_file:
        root_certificates = ca_file.read()

    server_credentials = grpc.ssl_server_credentials(
        [(private_key, certificate_chain)],
        root_certificates=root_certificates,
        require_client_auth=True,
    )
    server.add_secure_port("[::]:50051", server_credentials)
    await server.start()
    LOGGER.info("telemetry_ingestion_started")

    try:
        await server.wait_for_termination()
    finally:
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(serve())
