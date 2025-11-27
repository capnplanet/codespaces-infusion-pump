# Post-Deployment Monitoring & Evaluation

Contains scripts and dashboards for ongoing model performance monitoring, including drift detection and safety outcomes analysis. Outputs feed into CAPA processes and periodic regulatory reports.

## Components

- `monitor.py` — Batch job comparing live telemetry statistics with training baselines.
- `report_templates/` — Markdown/HTML templates for quarterly review packages.

All monitoring results must be archived with traceability to model versions and clinical environments.
