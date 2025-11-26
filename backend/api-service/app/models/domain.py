"""Domain models for regulated entities."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import AuditMixin, Base


class Patient(Base, AuditMixin):
    __tablename__ = "patients"

    mrn: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hashed_mrn: Mapped[str] = mapped_column(String(128), unique=True)
    demographics: Mapped[dict] = mapped_column(JSONB)

    sessions: Mapped[list["PumpSession"]] = relationship(back_populates="patient", cascade="all, delete-orphan")


class DeviceConfiguration(Base, AuditMixin):
    __tablename__ = "device_configurations"

    device_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    firmware_version: Mapped[str] = mapped_column(String(32))
    gateway_version: Mapped[str] = mapped_column(String(32))
    config_payload: Mapped[dict] = mapped_column(JSONB)


class DrugLibraryEntry(Base, AuditMixin):
    __tablename__ = "drug_library_entries"

    drug_name: Mapped[str] = mapped_column(String(64), index=True)
    concentration_mcg_per_ml: Mapped[float]
    min_rate_mcg_per_kg_min: Mapped[float]
    max_rate_mcg_per_kg_min: Mapped[float]
    max_delta_mcg_per_kg_min: Mapped[float]
    safety_notes: Mapped[str | None] = mapped_column(Text)


class PumpSession(Base, AuditMixin):
    __tablename__ = "pump_sessions"

    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    device_configuration_id: Mapped[int] = mapped_column(ForeignKey("device_configurations.id"))
    clinician_target_map_mmhg: Mapped[float]
    status: Mapped[str] = mapped_column(String(32), default="active")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    patient: Mapped[Patient] = relationship(back_populates="sessions")
    parameters: Mapped[list["ControlParameter"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class ControlParameter(Base, AuditMixin):
    __tablename__ = "control_parameters"

    session_id: Mapped[int] = mapped_column(ForeignKey("pump_sessions.id"))
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    payload: Mapped[dict] = mapped_column(JSONB)

    session: Mapped[PumpSession] = relationship(back_populates="parameters")


class MLModelVersion(Base, AuditMixin):
    __tablename__ = "ml_model_versions"

    registry_id: Mapped[str] = mapped_column(String(128), unique=True)
    version: Mapped[str] = mapped_column(String(32))
    dataset_hash: Mapped[str] = mapped_column(String(128))
    validation_report_path: Mapped[str] = mapped_column(String(256))
    acceptance_summary: Mapped[dict] = mapped_column(JSONB)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    actor: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(128))
    resource: Mapped[str] = mapped_column(String(256))
    before: Mapped[dict | None] = mapped_column(JSONB)
    after: Mapped[dict | None] = mapped_column(JSONB)
    metadata: Mapped[dict | None] = mapped_column(JSONB)
