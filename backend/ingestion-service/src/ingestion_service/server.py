"""gRPC server implementation for telemetry ingestion."""

from __future__ import annotations

import asyncio

import grpc
from aiokafka import AIOKafkaProducer
from structlog import get_logger

from . import telemetry_pb2, telemetry_pb2_grpc
from .config import get_settings

LOGGER = get_logger()


class TelemetryIngestionService(telemetry_pb2_grpc.TelemetryIngestionServicer):
    """Streams telemetry messages into Kafka topic."""

    def __init__(self, producer: AIOKafkaProducer, topic: str) -> None:
        self._producer = producer
        self._topic = topic

    async def StreamTelemetry(self, request_iterator, context):  # type: ignore[override]
        async for envelope in request_iterator:
            payload = envelope.SerializeToString()
            metadata = {
                "session_id": envelope.session_id,
                "device_id": envelope.device_id,
                "sequence": envelope.sequence,
            }
            await self._producer.send_and_wait(self._topic, payload, key=envelope.session_id.encode())
            LOGGER.info("telemetry_ingested", **metadata)
        return telemetry_pb2.TelemetryAck(accepted=True)


async def serve() -> None:
    settings = get_settings()
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)
    await producer.start()

    server = grpc.aio.server()
    try:
        telemetry_pb2_grpc.add_TelemetryIngestionServicer_to_server(
            TelemetryIngestionService(producer, settings.kafka_topic), server
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
