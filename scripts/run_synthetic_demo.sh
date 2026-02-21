#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

OUT_DIR="${1:-$ROOT_DIR/ml/pipelines/training/demo_artifacts}"
INGEST_TARGET="${INGEST_TARGET:-localhost:50051}"
DEVICE_API_KEY="${DEVICE_API_KEY:-change-me}"
DEMO_SESSIONS="${DEMO_SESSIONS:-60}"
DEMO_STEPS="${DEMO_STEPS:-24}"
INGEST_TLS_CA_CERT="${INGEST_TLS_CA_CERT:-}"
INGEST_TLS_CLIENT_CERT="${INGEST_TLS_CLIENT_CERT:-}"
INGEST_TLS_CLIENT_KEY="${INGEST_TLS_CLIENT_KEY:-}"

EXTRA_REPLAY_ARGS=()
if [[ -n "$INGEST_TLS_CA_CERT" ]]; then
  if [[ "$INGEST_TLS_CA_CERT" = /* ]]; then
    EXTRA_REPLAY_ARGS+=(--tls-ca-cert "$INGEST_TLS_CA_CERT")
  else
    EXTRA_REPLAY_ARGS+=(--tls-ca-cert "$ROOT_DIR/$INGEST_TLS_CA_CERT")
  fi
fi
if [[ -n "$INGEST_TLS_CLIENT_CERT" ]]; then
  if [[ "$INGEST_TLS_CLIENT_CERT" = /* ]]; then
    EXTRA_REPLAY_ARGS+=(--tls-client-cert "$INGEST_TLS_CLIENT_CERT")
  else
    EXTRA_REPLAY_ARGS+=(--tls-client-cert "$ROOT_DIR/$INGEST_TLS_CLIENT_CERT")
  fi
fi
if [[ -n "$INGEST_TLS_CLIENT_KEY" ]]; then
  if [[ "$INGEST_TLS_CLIENT_KEY" = /* ]]; then
    EXTRA_REPLAY_ARGS+=(--tls-client-key "$INGEST_TLS_CLIENT_KEY")
  else
    EXTRA_REPLAY_ARGS+=(--tls-client-key "$ROOT_DIR/$INGEST_TLS_CLIENT_KEY")
  fi
fi

cd "$ROOT_DIR/ml/pipelines/training"
python run_synthetic_demo.py --output-dir "$OUT_DIR" --dataset-format csv --sessions "$DEMO_SESSIONS" --steps "$DEMO_STEPS"

cd "$ROOT_DIR/edge/inference-service"
PYTHONPATH=src python -m edge_inference.replay_fixture \
  --fixture "$OUT_DIR/fixtures/telemetry_stream.jsonl" \
  --target "$INGEST_TARGET" \
  --api-key "$DEVICE_API_KEY" \
  "${EXTRA_REPLAY_ARGS[@]}"

echo "Synthetic demo completed. Artifacts: $OUT_DIR"
