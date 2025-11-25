# Closed-Loop Vasopressor Infusion Platform

This repository hosts the reference software stack for an AI-enabled, closed-loop vasopressor infusion control platform intended for ICU deployments. The architecture, assets, and documentation here are structured to maximize alignment with current FDA and GxP expectations for high-risk drug delivery. Actual regulatory approvals require tailored evidence, clinical data, and review by qualified regulatory professionals.

## Repository Layout

- `docs/` — Regulatory-aligned architecture, lifecycle, validation, and change-control documentation.
- `firmware/` — Real-time pump controller firmware (C/C++), deterministic safety logic, and hardware-in-the-loop tests.
- `edge/` — Bedside gateway services including Rust safety controller and Python ML inference microservice.
- `backend/` — On-prem/cloud API layer, telemetry ingestion, data persistence, and infrastructure-as-code.
- `ml/` — End-to-end ML pipelines, configuration, registries, and evaluation harnesses.
- `validation/` — Validation master plan assets, protocols, reports, and scripted evidence generation.
- `ops/` — Deployment manifests, IoT provisioning workflows, and cybersecurity hardening guides.

## Getting Started

1. Review `docs/architecture/system-architecture.md` for the end-to-end component diagram and trust boundaries.
2. Follow `docs/regulatory/compliance-matrix.md` to understand how the stack maps to FDA and ISO expectations.
3. Use `ops/k8s/platform-compose.yaml` and `ops/iot/gateway-bootstrap.md` as starting points for environment bring-up.
4. Execute ML pipelines via `ml/pipelines/training/README.md` after data access approvals are in place.
5. All development and change activities must follow the processes defined in `docs/validation/validation-master-plan.md` and `docs/change-control/continuous-change-control-plan.md`.

## Disclaimers

- The materials provided do **not** guarantee regulatory clearance. They are templates that must be tailored, verified, and approved by qualified clinical, engineering, cybersecurity, and regulatory teams.
- Safety-critical code paths are stubs; hardware integration, verification, and risk management analyses are mandatory before clinical use.
- Ensure compliance with hospital IT policies, cybersecurity requirements, and data governance regulations prior to deployment.
