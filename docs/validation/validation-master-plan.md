# Validation Master Plan (VMP)

This Validation Master Plan defines the risk-based approach for validating the closed-loop vasopressor infusion platform. The plan is structured to align with FDA expectations for computer software validation, ISO 13485:2016 quality management, GAMP 5 principles, 21 CFR Part 11, and ISO 14971 risk management. Final acceptance requires execution evidence and QA/RA approval.

## 1. Scope & Objectives

- **Systems in scope**: Pump firmware, bedside gateway safety controller, backend API & ingestion services, databases (PostgreSQL/TimescaleDB), ML pipelines, integration interfaces, identity/access services, observability stack, CI/CD tooling impacting released product, eQMS connectors.
- **Criticality tiers**:
  - Tier 1 (GxP-critical): Firmware, safety controller, configuration services, audit logging, security services, ML inference runtime.
  - Tier 2 (Supporting): Clinical dashboards, analytics, data warehouse replication, ML training environment.
  - Tier 3 (Non-GxP tools): Developer utilities, CI runners, monitoring visualization.
- **Objectives**: Demonstrate systems meet user requirements, mitigate risks to acceptable levels, ensure data integrity and Part 11 compliance, and maintain traceability from requirements to verification.

## 2. Validation Strategy

- Adopt V-model lifecycle per GAMP 5 with parallel risk management under ISO 14971.
- Deliverables per system:
  - URS, SDS/FDS, detailed design, risk assessment (FMEA/FTA), verification protocols, test reports, traceability matrices, cybersecurity documentation, ML-specific evidence (data management, algorithm description, PCCP bounds).
- Supplier assessments conducted for third-party components (RTOS, databases, libraries). Qualification reports stored under document control.
- Configuration management: all validated builds recorded with immutable identifiers and SBOM.

## 3. Testing Framework

- **Unit testing**: Firmware (Ceedling), Rust safety controller (cargo test), Python services (pytest); target ≥90% coverage for safety-critical modules.
- **Integration testing**: Hardware-in-the-loop bench linking firmware ↔ gateway; API integration harness verifying FHIR, gRPC, and override workflows.
- **System testing**: End-to-end scenarios covering normal operation, failover, fallback activation, cybersecurity events, and alarm handling.
- **Performance testing**: Throughput and latency under peak telemetry loads; worst-case 1 Hz vitals from 50 concurrent pumps per server node.
- **Security testing**: Threat modeling (STRIDE), vulnerability scanning, penetration testing, secure boot verification.
- **Usability testing**: Summative evaluation for clinician interface, adhering to FDA HFE/UE guidance.
- **ML validation**: Dataset integrity checks, model performance vs. acceptance criteria, sensitivity analyses, robustness evaluations, OOD detection effectiveness.
- **Regression testing**: Automated suite triggered on each change under change control.
- Deviations handled via standardized process: log, assess impact, assign CAPA, retest after remediation.

## 4. Documentation & Records

- All validation evidence stored in controlled repository (e.g., MasterControl) with unique document IDs and versioning.
- Part 11 compliance: audit trails capture creation, review, approval with timestamp, user ID, and meaning of signature.
- Traceability maintained in ALM tool linking URS → design → test cases → results → risk controls.
- Archived datasets and binaries stored in immutable storage with checksum verification.

## 5. Roles & Responsibilities

- **Development**: Produce design outputs, implement code, execute unit tests, supply traceability data.
- **QA/RA**: Own validation planning, approve protocols/reports, ensure compliance, manage audits.
- **Clinical Affairs**: Validate clinical relevance, oversee user validation and clinical trials.
- **Cybersecurity Team**: Maintain threat model, perform security testing, manage vulnerability disclosures.
- **ML Governance Board**: Approve datasets, models, PCCP adherence.
- **Change Control Board (CCB)**: Evaluate change requests, approve releases, ensure documentation closed.
- **Training**: Personnel in scope complete GxP, Part 11, and cybersecurity training before accessing systems.

## Maintenance

- VMP reviewed annually or upon significant system or regulatory changes.
- Outcomes of post-market surveillance and CAPA inform updates to validation scope and test coverage.
