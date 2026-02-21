# Infusion Spark UI

React + TypeScript console fully wired to the current FastAPI API service routes.

## Spark-elements parity model

This UI uses Spark-style primitives for parity-oriented behavior:

- Card-based surface hierarchy
- Compact labeled field blocks
- Primary/secondary action buttons
- Status pills for health/readiness
- Structured output panes for API responses

## Routes wired

- `GET /health`
- `POST /patients/`, `GET /patients/{id}`
- `POST /devices/configurations`, `GET /devices/configurations/{id}`
- `POST /sessions/`, `POST /sessions/{id}/close`
- `POST /drug-library/`, `GET /drug-library/{id}`
- `POST /ml-models/`, `GET /ml-models/{id}`
- `GET /audit/events`

## Run

```bash
cd frontend/spark-ui
npm install
npm run dev
```

Open `http://localhost:5173`.

Run with docker compose (from repo root):

```bash
docker compose up -d ui api postgres kafka ingestion
```

Use the **Connection & Auth** card to:

1. Set API base URL (default `/api`, proxied by Vite to backend API)
2. Generate a dev JWT from subject/roles/secret
3. Use the generated token for all protected endpoints

For local compose defaults, use secret `dev-insecure-jwt-secret`.
Proxy target can be overridden with `VITE_DEV_PROXY_TARGET` and initial base URL with `VITE_API_BASE_URL`.
