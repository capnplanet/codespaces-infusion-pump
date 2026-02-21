# Debt and Traceability Gap Report

Generated: 2026-02-21T13:08:28.770701+00:00

## Open Debt Items

- TD-001: HAL pump actuation/alarm functions are placeholders in pump HAL implementation. (Severity: High, Status: Open, Evidence: firmware/src/pump_hal.c)
- TD-002: Signed command and gateway message communication paths are placeholders. (Severity: High, Status: Open, Evidence: firmware/src/communication.c)
- TD-003: Telemetry streaming lacks retry/backoff/idempotency and outage durability policy. (Severity: High, Status: Open, Evidence: backend/ingestion-service/src/ingestion_service/server.py)
- TD-004: JWT claims handling lacks strict claim validation and role semantics in runtime authorization. (Severity: High, Status: In Progress, Evidence: backend/api-service/app/core/security.py)
- TD-005: Patient `hashed_mrn` previously stored raw MRN value. (Severity: High, Status: In Progress, Evidence: backend/api-service/app/routers/patients.py)
- TD-006: Prediction contract accepts weak feature validation and ambiguous confidence mapping. (Severity: High, Status: Open, Evidence: edge/inference-service/src/edge_inference/service.py)
- TD-007: Security/SBOM pipeline used soft-fail patterns for critical checks. (Severity: High, Status: In Progress, Evidence: .github/workflows/ci-sbom.yml)
- TD-008: Traceability and anomaly records contain unresolved placeholders/TBDs. (Severity: Medium, Status: Open, Evidence: docs/validation/traceability-matrix-template.csv)

## Traceability Rows With TBD

- NFR-SAFETY-LATENCY: Verification Artifact='performance tests (TBD)', Risk ID='RISK-HAZ-OVERINFUSION'
- NFR-SEC-MTLS: Verification Artifact='security test scripts (TBD)', Risk ID='RISK-HAZ-UNAUTHORIZEDACCESS'
- NFR-REL-INGESTION-RETRY: Verification Artifact='integration tests (TBD)', Risk ID='RISK-HAZ-TELEMETRYLOSS'
