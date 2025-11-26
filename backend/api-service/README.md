# Platform API Service

FastAPI-based service that manages configuration, audit logging, authentication, and telemetry ingestion for the infusion platform. Designed for deployment on hardened Kubernetes clusters with PostgreSQL backing store.

## Features

- Role-based access control (RBAC) with OAuth2/OIDC integration.
- Configuration endpoints for drug libraries, dosing constraints, and device provisioning.
- Immutable audit trail persistence supporting 21 CFR Part 11 requirements.
- WebSocket/gRPC bridges for real-time pump telemetry.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[test]
export API_SETTINGS__DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/infusion"
uvicorn app.main:app --reload
```

Refer to `docs/architecture/system-architecture.md` for trust boundaries. All runtime changes must follow the Validation Master Plan and Change Control Plan.
