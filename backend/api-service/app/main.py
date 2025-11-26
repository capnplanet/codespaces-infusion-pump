"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.settings import get_settings
from .routers import audit, devices, drug_library, health, ml_models, patients, sessions

settings = get_settings()
app = FastAPI(title="Infusion Platform API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(patients.router, prefix="/patients", tags=["patients"])
app.include_router(devices.router, prefix="/devices", tags=["devices"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
app.include_router(drug_library.router, prefix="/drug-library", tags=["drug-library"])
app.include_router(ml_models.router, prefix="/ml-models", tags=["ml-models"])
app.include_router(audit.router, prefix="/audit", tags=["audit"])
