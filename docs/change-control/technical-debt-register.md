# Technical Debt Register

This register tracks implementation debt items that are explicitly accepted, prioritized, and closed through change control.

## Usage

- Severity: `High`, `Medium`, `Low`
- Status: `Open`, `In Progress`, `Blocked`, `Closed`
- Every row must map to at least one requirement/test artifact and one owner.
- Closure requires: implemented code change, verification evidence, and traceability update.

## Debt Items

| ID | Component | Debt Description | Severity | Owner | Due | Status | Closure Criteria | Evidence Links |
|---|---|---|---|---|---|---|---|---|
| TD-001 | firmware | HAL pump actuation/alarm functions are placeholders in pump HAL implementation. | High | firmware lead | 2026-03-20 | Open | Replace placeholders, add unit/HIL tests, pass CI firmware gates. | firmware/src/pump_hal.c |
| TD-002 | firmware | Signed command and gateway message communication paths are placeholders. | High | firmware lead | 2026-03-20 | Open | Implement comms logic + auth checks + failure handling tests. | firmware/src/communication.c |
| TD-003 | backend/ingestion-service | Telemetry streaming lacks retry/backoff/idempotency and outage durability policy. | High | backend lead | 2026-03-15 | Open | Implement resilience policy, add failure injection tests, document contract. | backend/ingestion-service/src/ingestion_service/server.py |
| TD-004 | backend/api-service | JWT claims handling lacks strict claim validation and role semantics in runtime authorization. | High | backend lead | 2026-03-08 | In Progress | Enforce claim validation, role checks, add security tests. | backend/api-service/app/core/security.py |
| TD-005 | backend/api-service | Patient `hashed_mrn` previously stored raw MRN value. | High | backend lead | 2026-03-01 | In Progress | Salted one-way hashing implemented, migration strategy validated, tests updated. | backend/api-service/app/routers/patients.py |
| TD-006 | edge/inference-service | Prediction contract accepts weak feature validation and ambiguous confidence mapping. | High | ml/edge lead | 2026-03-22 | Open | Define confidence contract + strict validation + contract tests. | edge/inference-service/src/edge_inference/service.py |
| TD-007 | ci/security | Security/SBOM pipeline used soft-fail patterns for critical checks. | High | devops lead | 2026-02-28 | In Progress | Remove soft-fail behavior and enforce blocking CI checks. | .github/workflows/ci-sbom.yml |
| TD-008 | validation/docs | Traceability and anomaly records contain unresolved placeholders/TBDs. | Medium | qa/ra lead | 2026-03-29 | Open | Link open debt to verification artifacts and close TBD entries. | docs/validation/traceability-matrix-template.csv |
