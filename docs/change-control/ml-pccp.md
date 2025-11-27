# ML Predetermined Change Control Plan (PCCP)

## SaMD Pre-Specifications (SPS)

- Allow retraining using approved ICU cohorts collected under data governance SOP.
- Permit feature set adjustments limited to existing vital signs, labs, demographics, and dosing history ontologies.
- Hyperparameter tuning constrained to ranges documented in `ml/config/acceptance-criteria.yaml`.
- Calibration layer adjustments using isotonic regression or Platt scaling may be performed.

## Algorithm Change Protocol (ACP)

1. Initiate change request with rationale, dataset version, and proposed parameter updates.
2. Execute reproducible training pipeline (`ml/pipelines/training/train.py`) referencing controlled config.
3. Validate new model against acceptance criteria, robustness tests, and bias analysis checklist.
4. Update model card, validation report, and risk assessment.
5. Obtain approvals from ML governance board, QA/RA, and clinical safety officer.
6. Deploy via staged rollout (shadow → limited release) with monitoring triggers.

## Exit Criteria

- If AUROC change exceeds ±5%, calibration slope exits [0.9, 1.1], or new features involve previously unused data classes, change exits PCCP and requires regulatory submission.
- Any modifications affecting safety controller interfaces or confidence reporting require premarket notification.
