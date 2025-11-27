#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="${SCRIPT_DIR}/.."
PROTO_DIR="${ROOT_DIR}/proto"
OUT_DIR="${ROOT_DIR}/src/ingestion_service"

python -m grpc_tools.protoc -I"${PROTO_DIR}" --python_out="${OUT_DIR}" --grpc_python_out="${OUT_DIR}" "${PROTO_DIR}/telemetry.proto"
echo "Generated gRPC code in ${OUT_DIR}" 