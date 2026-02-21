#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

OUT_DIR="${1:-$ROOT_DIR/ml/pipelines/training/demo_artifacts}"
INGEST_TARGET="${INGEST_TARGET:-localhost:50051}"
DEVICE_API_KEY="${DEVICE_API_KEY:-change-me}"
DEMO_SESSIONS="${DEMO_SESSIONS:-60}"
DEMO_STEPS="${DEMO_STEPS:-24}"

cd "$ROOT_DIR/ml/pipelines/training"
python run_synthetic_demo.py --output-dir "$OUT_DIR" --dataset-format csv --sessions "$DEMO_SESSIONS" --steps "$DEMO_STEPS"

cd "$ROOT_DIR/edge/inference-service"
PYTHONPATH=src python -m edge_inference.replay_fixture \
  --fixture "$OUT_DIR/fixtures/telemetry_stream.jsonl" \
  --target "$INGEST_TARGET" \
  --api-key "$DEVICE_API_KEY"

echo "Synthetic demo completed. Artifacts: $OUT_DIR"
