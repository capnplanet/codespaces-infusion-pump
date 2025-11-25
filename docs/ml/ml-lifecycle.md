# ML Lifecycle Blueprint

This blueprint outlines the total product lifecycle (TPLC) process for the MAP prediction and hypotension risk models supporting the infusion platform. It aims to maximize compliance with FDA AI-DSF draft guidance, ISO 14971 risk management, and internal QMS expectations. Regulatory acceptance requires qualified review and supporting evidence.

## Problem Definition

- **Clinical objective**: Predict 5–10 minute MAP trajectory and hypotension risk for ICU sepsis patients receiving vasopressors.
- **Role in control loop**: Provide forecast, risk score, and confidence interval to deterministic safety controller. Low confidence or anomaly triggers fallback protocol.
- **Inputs**: Vital sign streams (MAP, HR, SpO2), lab values, demographics, comorbidities, infusion history, clinician targets.
- **Outputs**: MAP forecast curve, hypotension probability, confidence metrics, feature attributions.

## Data Governance

1. Data sources captured via secure interfaces (HL7, FHIR, pump logs) and staged in governed Delta Lake.
2. De-identification using HIPAA-compliant transforms; linkage keys stored separately under restricted access.
3. Dataset versioning handled through DVC tracked in Git; metadata managed in DataHub with lineage reporting.
4. Bias and representativeness analyses run per cohort; results documented in `ml/registry/model-cards/`.

## Model Development

- Algorithm choice: Ensemble of gradient boosted trees (XGBoost) on tabular aggregates and Temporal Convolutional Network on raw sequences; outputs combined via calibration layer.
- Training: Patient-level stratified splits (70/15/15) with nested cross-validation; hyperparameter sweeps logged in MLflow.
- Metrics: AUROC/AUPRC for hypotension classification, MAE for MAP forecasts, calibration slope, time-in-target simulation outputs.
- Explainability: SHAP summaries for tabular features, saliency for temporal encoder; included in validation dossiers.

## Verification & Validation

- Offline replay tests with historical sessions to verify controller decisions under simulated automation.
- Stress testing: Sensor dropout, noise injection, extreme physiologies; ensure confidence fallbacks trigger.
- Security review: Adversarial perturbation resistance and data poisoning detection.
- Acceptance criteria defined in `ml/config/acceptance-criteria.yaml`; deviations require risk assessment.

## Deployment & Monitoring

- CI/CD pipeline executes unit tests (`pytest`), data validation (`great_expectations`), and reproducibility checks prior to registry promotion.
- Staged rollout: shadow mode → limited release under IDE → full deployment; performance dashboards monitored in Grafana.
- Drift detection: PSI for feature drift, rolling AUROC for performance; automatic alerts to ML governance board.
- Change management aligned with PCCP; retraining inside defined bounds documented in `docs/change-control/ml-pccp.md`.

## Documentation & Records

- Model cards, dataset datasheets, validation reports stored under document control.
- All pipeline runs linked to requirements IDs in ALM system via MLflow tags.
- Electronic signatures captured for approvals per Part 11 requirements.
