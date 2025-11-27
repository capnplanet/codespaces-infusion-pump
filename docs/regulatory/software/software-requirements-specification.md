# Software Requirements Specification (SRS)

Document ID: SW-SRS
Version: 0.1 (Draft)
Effective Date: TBD
Owner: Systems Engineering
Approver: TBD
Change History: v0.1 Initial scaffold

## 1. Purpose
Defines functional and non-functional software requirements for the Closed-Loop Vasopressor Infusion Platform.

## 2. References
- `docs/architecture/requirements-overview.md`
- `docs/architecture/system-architecture.md`
- ISO 14971:2019, IEC 62304:2006+A1:2015, FDA 2021 Software Guidance

## 3. Definitions and Abbreviations
Provide domain-specific definitions (TBD).

## 4. System Context
Summarize components and interfaces; reference `docs/architecture/system-architecture.md`.

## 5. Functional Requirements
- FR-001: The safety controller shall enforce minimum/maximum infusion rate limits defined in the drug library. Source: `firmware/include/safety_controller.h`; verification: unit tests in `firmware/tests/`.
- FR-002: The edge safety controller shall command fallback dose when ML confidence < threshold. Source: `edge/safety-controller/src/lib.rs`; verification: `edge/safety-controller/tests/`.
- FR-003: The inference service shall expose a `/predict` API returning dose suggestion with confidence and rationale. Source: `edge/inference-service/src/edge_inference/service.py`; verification: `edge/inference-service/tests/`.
- FR-004: The backend shall store patient, device, session, drug library, and ML model metadata. Source: `backend/api-service/app/models/`; verification: API tests in `backend/api-service/tests/`.
- FR-005: The ingestion service shall accept gRPC telemetry and publish to Kafka with idempotent keys. Source: `backend/ingestion-service/src/ingestion_service/server.py`; verification: integration tests (TBD).

- FR-006: The backend API shall expose an audit endpoint capturing actor, action, resource, before/after states for regulated operations. Source: `backend/api-service/app/routers/audit.py`; verification: API tests (TBD).
- FR-007: The drug library management shall restrict modification endpoints to authorized clinical roles (RBAC). Source: `backend/api-service/app/routers/drug_library.py`; verification: security tests (TBD).
- FR-008: The inference service shall reject requests with missing required vital sign parameters and return validation errors. Source: `edge/inference-service/src/edge_inference/service.py`; verification: negative tests (TBD).
- FR-009: The ingestion service shall log telemetry ingestion events with session and sequence identifiers. Source: `backend/ingestion-service/src/ingestion_service/server.py`; verification: log inspection tests (TBD).
- FR-010: The system shall support versioned ML model metadata tracked in `ml_model_versions` with dataset hash and acceptance summary. Source: `backend/api-service/app/models/domain.py`; verification: API tests (TBD).
- FR-011: The safety controller shall raise an alarm condition when commanded rate exceeds allowed delta change. Source: `firmware/include/safety_controller.h`; verification: unit/HIL tests (TBD).
- FR-012: The system shall provide a session termination operation updating `pump_sessions.ended_at` and status. Source: `backend/api-service/app/routers/sessions.py`; verification: API tests (TBD).
- FR-013: The telemetry ingestion shall persist last sequence number per session (future feature placeholder). Source: planned storage component (TBD); verification: integration tests (future).
- FR-014: The system shall record configuration changes to `device_configurations` with audit entries. Source: `backend/api-service/app/models/domain.py`; verification: API + audit tests (TBD).

Add additional requirements as design matures.

## 6. Non-Functional Requirements
- Safety: Deterministic fallback response within bounded latency.
- Security: mTLS for all inter-service communications; signed artifacts.
- Performance: Inference latency p95 ≤ TBD ms on target hardware.
- Reliability: Ingestion tolerates transient broker failures (retry/backoff).
- Usability: Clinician UI presents current dose, alarms, and override safely.

- Maintainability: Code components shall include automated CI lint/test workflows per language before merge. Source: `.github/workflows/`.
- Observability: Services shall emit structured logs with session/device identifiers (JSON or key-value). Source: logging configuration (TBD).
- Availability: Core API shall handle rolling updates without downtime (K8s readiness/liveness probes). Source: deployment manifests (future).
- Scalability: Kafka-based ingestion shall decouple telemetry input from backend persistence enabling horizontal scaling. Source: `backend/ingestion-service` design.
- Data Integrity: All patient identifiers shall be stored hashed (`hashed_mrn`) alongside pseudonymized records. Source: `backend/api-service/app/models/domain.py`.

## 7. Constraints and Assumptions
- Edge hardware resources are constrained; real-time safety logic must not block.
- Hospital IT policies require certificate-based auth and network segmentation.

## 8. Traceability
Each requirement shall map to design, implementation, risks, and tests in `docs/validation/traceability-matrix-template.csv`.
