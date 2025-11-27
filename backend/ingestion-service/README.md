# Telemetry Ingestion Service

Asynchronous gRPC service that accepts telemetry streams from bedside gateways and publishes them to the secure backend event bus (Kafka). Designed for deployment within the hospital data center or secure cloud segment.

## Key Responsibilities

- Authenticate edge gateways via mutual TLS and per-device API keys.
- Validate telemetry payloads against protobuf schema and schema registry constraints.
- Buffer and retry writes to Kafka with deterministic backoff.
- Forward high-severity safety events to the audit API.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[test]
python -m grpc_tools.protoc -I proto --python_out=src --grpc_python_out=src proto/telemetry.proto
pytest
```

Runtime configuration is managed via environment variables described in `src/ingestion_service/config.py`. Production deployments must enable mutual TLS and run within a network segment restricted to authenticated gateways.
