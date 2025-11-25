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
