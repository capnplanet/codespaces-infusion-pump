# Software Architecture & Design Specification (SDS)

Document ID: SW-SDS
Version: 0.1 (Draft)
Effective Date: TBD
Owner: Software Architecture
Approver: TBD
Change History: v0.1 Initial scaffold

## 1. Overview
Architecture of firmware, edge, and backend services and detailed design of critical components.

## 2. References
- `docs/architecture/system-architecture.md`
- `docs/regulatory/software-description.md`

## 3. Architecture
- Components: firmware controller (`firmware/`), edge safety controller (`edge/safety-controller`), inference service (`edge/inference-service`), API (`backend/api-service`), ingestion (`backend/ingestion-service`).
- Trust boundaries: per `docs/architecture/system-architecture.md`.

## 4. Detailed Designs
- Safety Controller (Firmware and Rust): rate clamp, ramp limits, confidence gating; interfaces to HAL/comms.
- Inference Service: ONNX runtime wrapper, input validation, timeout guards, telemetry client.
- API Service: domain models, routers, async DB engine; JWT/OIDC security utilities.
- Ingestion Service: gRPC server, Kafka producer, TLS configuration.

## 5. Interfaces and Data Models
- REST schemas: `backend/api-service/app/schemas/`
- gRPC: `backend/ingestion-service/proto/telemetry.proto`

## 6. SOUP and Dependencies
See `docs/regulatory/software/soup-inventory.md`.

## 7. Design Decisions and Rationale
Document safety partitioning, deterministic fallbacks, and model-gating rationale.

## 8. Risks and Controls Linkage
Link to `docs/regulatory/risk/hazard-analysis.md` for risk-driven design controls.
