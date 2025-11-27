# Software Development Plan (SDP)

Document ID: SW-SDP
Version: 0.1 (Draft)
Effective Date: TBD
Owner: Software Lead
Approver: TBD
Change History: v0.1 Initial scaffold

## Purpose and Scope
Defines processes, responsibilities, and environments for developing the software components of the Closed-Loop Vasopressor Infusion Platform in alignment with IEC 62304 and FDA expectations.

## Applicable Standards and Guidance
- IEC 62304:2006+A1:2015 — Software life cycle processes
- ISO 14971:2019 — Risk management
- FDA: Content of Premarket Submissions for Device Software Functions (2021)
- 21 CFR 820 — QSR (process controls, design controls, CAPA)

## Software Items and Configuration
- Firmware: `firmware/` (C/C++, CMake)
- Edge Safety Controller: `edge/safety-controller/` (Rust)
- Edge Inference Service: `edge/inference-service/` (Python)
- Backend API: `backend/api-service/` (Python)
- Ingestion Service: `backend/ingestion-service/` (Python gRPC)

## Life Cycle Processes
- Planning: This SDP, Design & Development Plan (`docs/validation/design-control-plan.md`)
- Requirements: SRS (`docs/regulatory/software/software-requirements-specification.md`), requirements overview (`docs/architecture/requirements-overview.md`)
- Architecture/Design: SDS (`docs/regulatory/software/software-architecture-design-specification.md`), `docs/architecture/system-architecture.md`
- Implementation: Coding standards, code review, static analysis per component sections
- Verification: SVVP (`docs/regulatory/software/software-verification-validation-plan.md`)
- Validation: `docs/validation/validation-master-plan.md`
- Risk: `docs/regulatory/risk/hazard-analysis.md`, `docs/regulatory/risk/risk-acceptability-criteria.md`
- Configuration & Problem Resolution: `docs/regulatory/software/configuration-management-plan.md`, `docs/regulatory/software/problem-anomaly-report.md`
- Release: `docs/regulatory/software/version-description-document.md`

## Development Environment
- Source Control: Git (GitHub), branching strategy and protected main
- CI/CD: GitHub Actions (linters, unit tests, SBOM, SAST)
- Build Tools: CMake (firmware), Cargo (Rust), Poetry/uv/pip (Python)
- Issue Tracking: TBD (link to tracker)

## Software Safety Classification
Intended per IEC 62304; classification rationale recorded in `docs/regulatory/software/documentation-level.md` and risk files.

## Deliverables
- SRS, SDS, SVVP/SVVR, RMF updates, Traceability Matrix, Release Notes, SOUP list.

## Reviews and Approvals
- Design reviews at milestones; documented in meeting minutes and PR approvals.

## Change Control
- Follow `docs/change-control/continuous-change-control-plan.md` and eQMS procedures.
