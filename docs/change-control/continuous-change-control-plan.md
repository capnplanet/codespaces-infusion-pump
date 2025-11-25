# Continuous Change Control Plan

This plan governs lifecycle changes to traditional software and ML components of the infusion platform. It reflects FDA AI-DSF draft PCCP expectations, 21 CFR 820 design control, ISO 13485, ISO 14971, and GAMP 5 best practices. Regulatory submissions remain subject to formal review; this plan must be tailored and approved by QA/RA.

## 1. Change Categories

- **Minor**: UI text updates, analytics dashboards, non-safety reporting adjustments (no impact to safety or data integrity). Document in change log, QA notification optional.
- **Moderate**: Performance optimizations, refactoring within validated boundaries, ML retraining within SaMD Pre-Specifications, security patches without functionality change. Requires impact assessment, targeted testing, QA approval.
- **Major**: Safety controller modifications, dose limit changes, new data sources, ML architecture alterations beyond PCCP bounds, expanded indications. Requires full design control cycle, risk re-evaluation, potential regulatory submission (510(k)/PMA supplement/De Novo).

## 2. Predetermined Change Control Plan (PCCP) for ML

- **SaMD Pre-Specifications (SPS)**: Allow retraining with approved ICU cohorts, feature expansions within defined ontology, hyperparameter adjustments inside documented ranges, calibration layer tuning. Changes must maintain performance within acceptance criteria defined in `ml/config/acceptance-criteria.yaml`.
- **Algorithm Change Protocol (ACP)**:
  1. Initiation with change request referencing dataset and code revisions.
  2. Data quality checks and bias analyses compared against baseline.
  3. Training pipeline execution with reproducibility evidence (MLflow reports, DVC hashes).
  4. Validation: statistical comparison to reference model, robustness suite, cybersecurity review.
  5. Documentation: updated model card, risk assessment, traceability matrix.
  6. Approval: ML governance board + QA/RA sign-off, evaluate regulatory impact against SPS criteria.
- **Trigger for regulatory submission**: Performance deviation beyond predefined bounds, new indicators or control outputs, material change to uncertainty estimation, new patient population outside original labeling.

## 3. Change Workflow

1. **Request**: Submit change in ALM with description, rationale, classification, linked requirements.
2. **Impact Assessment**: Evaluate risk (ISO 14971), cybersecurity (threat model update), validation scope, and regulatory implications.
3. **Approval**: Change Control Board reviews, ensures required documentation present, records Part 11-compliant signatures.
4. **Implementation**: Development under configuration management, feature branches tied to change ID, automated tests executed.
5. **Verification & Validation**: Run required test suites (unit, integration, system, ML validation). Record results in controlled repository.
6. **Release**: QA/RA issues release authorization, ops deploys via controlled pipeline ensuring signed artifacts and SBOM updates.
7. **Documentation Closure**: Update DHF/DMR, traceability, and training records if applicable.

## 4. Post-Change Monitoring

- Defined observation window (default 30 days) with automated telemetry dashboards tracking safety metrics, overrides, adverse events, cybersecurity alerts.
- Daily review by operations and clinical leads; anomalies trigger CAPA investigation and potential rollback.
- Quarterly management review summarizes changes, outcomes, outstanding risks, and regulatory status.

## 5. Tools & Records

- Change tracking in Polarion or similar ALM with immutable audit history.
- Electronic signatures via Part 11-compliant eQMS (e.g., MasterControl) referencing change ID.
- SBOM maintained in `ops/security/sbom-template.cdx`; updated with each release.
- Documentation artifacts (test reports, risk updates, approvals) stored under document control with versioning.

## 6. Assumptions

- Organization maintains staffed CCB with representation from engineering, QA/RA, clinical, cybersecurity, and ML governance.
- Deployment pipeline supports signed binaries (Sigstore, in-toto attestations).
- Hospital IT partners agree to scheduled maintenance windows and rollback procedures.
