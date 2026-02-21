# Closed-Loop Vasopressor Infusion Platform

Reference implementation for an AI-assisted, closed-loop vasopressor infusion stack spanning firmware, edge safety/inference, backend services, ML pipelines, and regulatory/validation documentation.

This repository is designed for engineering development, integration testing, and evidence scaffolding. It is not production-ready for clinical deployment without additional implementation, verification, and regulatory completion work.

## Current Capability Snapshot

### Implemented

- Backend API foundations: patient/device/session/model endpoints with JWT claim validation and RBAC enforcement.
- Ingestion service hardening: retry/backoff, idempotency by sequence, gateway API-key checks, safety alarm forwarding.
- Edge inference hardening: stricter feature contracts, confidence contract validation, gRPC telemetry bridge to ingestion.
- Safety controller hardening: aligned confidence/range fallback behavior in both Rust gateway controller and firmware controller.
- Synthetic demo scaffolding: deterministic synthetic dataset generation, telemetry fixture generation, fixture replay tooling.
- Debt governance automation: technical debt register synchronization into anomaly and traceability gap reporting.

### In Progress / Partial

- End-to-end deployment wiring for all services in one production-like environment.
- ML artifact handoff from training to signed ONNX deployment package.
- Full validation evidence closure for traceability rows currently marked as TBD.

### Not Yet Production Complete

- Hardware integration completeness for all firmware HAL/comms paths.
- Full security hardening and operational controls (PKI lifecycle, key rotation, secrets governance).
- Comprehensive system-level performance, cybersecurity, and HIL verification evidence for release.
- Regulatory package completion and controlled approval workflow closure.

## Repository Layout

- [docs](docs) — Architecture, design control, risk, regulatory, and change-control artifacts.
- [backend](backend) — API service, telemetry ingestion service, infra migration assets.
- [edge](edge) — Rust safety controller and Python inference service.
- [firmware](firmware) — Pump controller firmware and C safety logic/tests.
- [ml](ml) — Training/evaluation pipelines and ML acceptance criteria.
- [validation](validation) — Validation plans, protocols, reports, and helper scripts.
- [ops](ops) — Environment and platform deployment assets.

## Synthetic Demo Pipeline

Generate synthetic training data and telemetry fixtures:

```bash
cd ml/pipelines/training
python run_synthetic_demo.py --output-dir demo_artifacts --dataset-format csv
```

Replay generated fixture to ingestion over gRPC:

```bash
cd edge/inference-service
PYTHONPATH=src python -m edge_inference.replay_fixture \
	--fixture ../../ml/pipelines/training/demo_artifacts/fixtures/telemetry_stream.jsonl \
	--target localhost:50051 \
	--api-key <device-api-key>
```

Or run both steps with one command:

```bash
DEVICE_API_KEY=<device-api-key> INGEST_TARGET=localhost:50051 ./scripts/run_synthetic_demo.sh
```

## Test Execution

API service:

```bash
cd backend/api-service
API_SETTINGS__DATABASE_URL=sqlite+aiosqlite:///:memory: API_SETTINGS__JWT_SECRET_KEY=test-secret PYTHONPATH=. python -m pytest -q
```

Ingestion service:

```bash
cd backend/ingestion-service
PYTHONPATH=src python -m pytest -q
```

Edge inference service:

```bash
cd edge/inference-service
PYTHONPATH=src python -m pytest -q
```

Rust safety controller:

```bash
cd edge/safety-controller
cargo test -q
```

Firmware safety test:

```bash
cd firmware
cmake -S . -B build && cmake --build build && ctest --test-dir build --output-on-failure
```

## Production Readiness Position

Current state is best described as integration-ready development baseline with meaningful safety/security hardening in place, but not release-ready for patient care use.

Use [docs/change-control/technical-debt-register.md](docs/change-control/technical-debt-register.md), [docs/regulatory/software/problem-anomaly-report.md](docs/regulatory/software/problem-anomaly-report.md), and [validation/reports/debt-traceability-gap-report.md](validation/reports/debt-traceability-gap-report.md) as the canonical open-item trackers.

## Regulatory and Safety Disclaimer

This repository does not constitute FDA clearance, CE marking, or authorization for clinical use. Clinical deployment requires complete risk controls, verified performance/safety evidence, cybersecurity compliance, quality-system controls, and formal regulatory review/approval.
