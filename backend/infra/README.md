# Infrastructure as Code

This directory aggregates infrastructure artifacts for deploying the backend platform in hospital-controlled environments.

## Contents

- `migrations/` — Alembic migrations (SQL + Python) defining the regulated relational schema.
- `helm/` — Helm charts (future work) for Kubernetes deployment.
- `terraform/` — Infrastructure provisioning templates (e.g., private networking, managed PostgreSQL, Kafka clusters).

## Usage

1. Initialize Alembic environment using `alembic init migrations` (already bootstrapped). Ensure migrations reference the production database DSN under change control.
2. Apply migrations in lower environments first, capture verification evidence, then promote.
3. Helm/Terraform modules must go through validation and cybersecurity review prior to production changes.
