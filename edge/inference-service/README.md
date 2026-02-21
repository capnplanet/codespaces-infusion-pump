# Edge Inference Service

Python microservice deployed on the bedside gateway to execute ONNX MAP prediction models, perform confidence checks, and hand structured outputs to the Rust safety controller.

## Features

- Loads signed ONNX models from secure storage with integrity verification.
- Provides local REST/gRPC endpoint for safety controller ingestion.
- Publishes predictions and metadata to backend telemetry service for audit.
- Enforces deterministic timeouts and confidence thresholds before returning results.

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[test]
pytest
```

Configuration parameters are defined in `src/edge_inference/config.py` and can be overridden by environment variables or a `.env` file. All changes require verification evidence per the Validation Master Plan.

## Telemetry Bridge Modes

Telemetry publish supports two transport modes:

- `EDGE_INFER_TELEMETRY_TRANSPORT=http` (default): publishes to `EDGE_INFER_TELEMETRY_ENDPOINT`.
- `EDGE_INFER_TELEMETRY_TRANSPORT=grpc`: publishes directly to ingestion gRPC target `EDGE_INFER_TELEMETRY_GRPC_TARGET` using the telemetry contract in `proto/telemetry.proto`.

For gRPC mode, configure:

- `EDGE_INFER_TELEMETRY_API_KEY`
- `EDGE_INFER_TELEMETRY_DEVICE_ID`
- `EDGE_INFER_TELEMETRY_SESSION_ID`

Replay generated synthetic fixture JSONL directly to ingestion:

```bash
PYTHONPATH=src python -m edge_inference.replay_fixture \
	--fixture ../../ml/pipelines/training/demo_artifacts/fixtures/telemetry_stream.jsonl \
	--target localhost:50051 \
	--api-key <device-api-key>
```
