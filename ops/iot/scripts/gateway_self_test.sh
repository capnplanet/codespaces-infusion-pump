#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
STACK_FILE="${STACK_FILE:-$ROOT_DIR/docker-compose.yml}"
CERT_DIR="${CERT_DIR:-$ROOT_DIR/ops/iot/certs/dev}"
LOG_DIR="${LOG_DIR:-$ROOT_DIR/ops/iot/self-test-logs}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
LOG_FILE="$LOG_DIR/gateway-self-test-$TIMESTAMP.log"

mkdir -p "$LOG_DIR"

echo "[self-test] stack file: $STACK_FILE" | tee -a "$LOG_FILE"
echo "[self-test] cert dir:   $CERT_DIR" | tee -a "$LOG_FILE"

if ! command -v docker >/dev/null 2>&1; then
  echo "[self-test] FAIL: docker not found on PATH" | tee -a "$LOG_FILE"
  exit 1
fi

if ! command -v openssl >/dev/null 2>&1; then
  echo "[self-test] FAIL: openssl not found on PATH" | tee -a "$LOG_FILE"
  exit 1
fi

if [[ ! -f "$CERT_DIR/ca.crt" || ! -f "$CERT_DIR/server.crt" || ! -f "$CERT_DIR/server.key" ]]; then
  echo "[self-test] certs missing, generating dev mTLS certs" | tee -a "$LOG_FILE"
  "$ROOT_DIR/ops/iot/scripts/generate_dev_certs.sh" "$CERT_DIR" | tee -a "$LOG_FILE"
fi

for cert in ca.crt server.crt server.key client.crt client.key; do
  if [[ ! -f "$CERT_DIR/$cert" ]]; then
    echo "[self-test] FAIL: missing certificate artifact $CERT_DIR/$cert" | tee -a "$LOG_FILE"
    exit 1
  fi
done

echo "[self-test] bringing up compose services" | tee -a "$LOG_FILE"
docker compose -f "$STACK_FILE" up -d postgres kafka api ingestion | tee -a "$LOG_FILE"

echo "[self-test] waiting for API health endpoint" | tee -a "$LOG_FILE"
for _ in $(seq 1 30); do
  if curl -fsS "http://localhost:8000/health" >/dev/null 2>&1; then
    echo "[self-test] API reachable" | tee -a "$LOG_FILE"
    break
  fi
  sleep 1
done

if ! curl -fsS "http://localhost:8000/health" >/dev/null 2>&1; then
  echo "[self-test] FAIL: API health endpoint not reachable" | tee -a "$LOG_FILE"
  exit 1
fi

echo "[self-test] verifying ingestion mTLS channel" | tee -a "$LOG_FILE"
for _ in $(seq 1 45); do
  if timeout 2 bash -c "echo >/dev/tcp/127.0.0.1/50051" 2>/dev/null; then
    break
  fi
  sleep 1
done

if ! timeout 5 bash -c "echo >/dev/tcp/127.0.0.1/50051" 2>/dev/null; then
  echo "[self-test] FAIL: ingestion port 50051 is not open" | tee -a "$LOG_FILE"
  exit 1
fi

if ! docker compose -f "$STACK_FILE" exec -T ingestion python - <<'PY' >>"$LOG_FILE" 2>&1
import grpc

ca = open('/certs/ca.crt', 'rb').read()
cert = open('/certs/client.crt', 'rb').read()
key = open('/certs/client.key', 'rb').read()

credentials = grpc.ssl_channel_credentials(
    root_certificates=ca,
    private_key=key,
    certificate_chain=cert,
)
channel = grpc.secure_channel('ingestion:50051', credentials)
grpc.channel_ready_future(channel).result(timeout=5)
channel.close()
print('ingestion_mtls_ready')
PY
then
  echo "[self-test] FAIL: ingestion mTLS channel readiness check failed" | tee -a "$LOG_FILE"
  exit 1
fi

echo "[self-test] verifying ingestion API-key enforcement" | tee -a "$LOG_FILE"
if ! docker compose -f "$STACK_FILE" exec -T ingestion python - <<'PY' >>"$LOG_FILE" 2>&1
import grpc

from ingestion_service import telemetry_pb2, telemetry_pb2_grpc

ca = open('/certs/ca.crt', 'rb').read()
cert = open('/certs/client.crt', 'rb').read()
key = open('/certs/client.key', 'rb').read()

credentials = grpc.ssl_channel_credentials(
  root_certificates=ca,
  private_key=key,
  certificate_chain=cert,
)

channel = grpc.secure_channel('ingestion:50051', credentials)
grpc.channel_ready_future(channel).result(timeout=5)
stub = telemetry_pb2_grpc.TelemetryIngestionStub(channel)

envelope = telemetry_pb2.TelemetryEnvelope(
  session_id='self-test-session',
  device_id='pump-00',
  sequence=1,
)

try:
  stub.StreamTelemetry(
    iter([envelope]),
    metadata=(('x-api-key', 'wrong-key'), ('x-device-id', 'pump-00')),
    timeout=3,
  )
  raise RuntimeError('expected UNAUTHENTICATED for invalid API key')
except grpc.RpcError as exc:
  if exc.code() != grpc.StatusCode.UNAUTHENTICATED:
    raise

ack = stub.StreamTelemetry(
  iter([
    telemetry_pb2.TelemetryEnvelope(
      session_id='self-test-session',
      device_id='pump-00',
      sequence=2,
    )
  ]),
  metadata=(('x-api-key', 'change-me'), ('x-device-id', 'pump-00')),
  timeout=3,
)

if not ack.accepted:
  raise RuntimeError('ingestion did not accept valid API-key envelope')

channel.close()
print('ingestion_api_key_enforced')
PY
then
  echo "[self-test] FAIL: ingestion API-key enforcement check failed" | tee -a "$LOG_FILE"
  exit 1
fi

echo "[self-test] PASS: gateway software bootstrap checks completed" | tee -a "$LOG_FILE"
echo "[self-test] log: $LOG_FILE"
