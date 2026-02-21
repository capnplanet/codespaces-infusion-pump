#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/certs/dev}"
mkdir -p "$OUT_DIR"

CA_KEY="$OUT_DIR/ca.key"
CA_CERT="$OUT_DIR/ca.crt"
SERVER_KEY="$OUT_DIR/server.key"
SERVER_CSR="$OUT_DIR/server.csr"
SERVER_CERT="$OUT_DIR/server.crt"
CLIENT_KEY="$OUT_DIR/client.key"
CLIENT_CSR="$OUT_DIR/client.csr"
CLIENT_CERT="$OUT_DIR/client.crt"

openssl req -x509 -newkey rsa:2048 -sha256 -days 365 -nodes \
  -subj "/CN=infusion-dev-ca" \
  -keyout "$CA_KEY" \
  -out "$CA_CERT" >/dev/null 2>&1

openssl req -newkey rsa:2048 -nodes \
  -subj "/CN=ingestion" \
  -keyout "$SERVER_KEY" \
  -out "$SERVER_CSR" >/dev/null 2>&1

openssl x509 -req -in "$SERVER_CSR" -CA "$CA_CERT" -CAkey "$CA_KEY" -CAcreateserial \
  -out "$SERVER_CERT" -days 365 -sha256 \
  -extfile <(printf "subjectAltName=DNS:ingestion,DNS:localhost,IP:127.0.0.1") >/dev/null 2>&1

openssl req -newkey rsa:2048 -nodes \
  -subj "/CN=edge-gateway" \
  -keyout "$CLIENT_KEY" \
  -out "$CLIENT_CSR" >/dev/null 2>&1

openssl x509 -req -in "$CLIENT_CSR" -CA "$CA_CERT" -CAkey "$CA_KEY" -CAcreateserial \
  -out "$CLIENT_CERT" -days 365 -sha256 >/dev/null 2>&1

rm -f "$SERVER_CSR" "$CLIENT_CSR" "$OUT_DIR/ca.srl"

echo "Generated development certificates in $OUT_DIR"
