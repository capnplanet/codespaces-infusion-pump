"""Device and configuration models."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import AuditMixin, Base


class EdgeDevice(Base, AuditMixin):
    __tablename__ = "edge_devices"

    serial_number: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="inactive")
    location: Mapped[str] = mapped_column(String(128))

    sessions: Mapped[list[PumpSession]] = relationship(back_populates="device")


class PumpSession(Base, AuditMixin):
    __tablename__ = "pump_sessions"

    device_id: Mapped[int] = mapped_column(ForeignKey("edge_devices.id"))
    patient_id: Mapped[str] = mapped_column(String(64))  # references hashed patient identifier
    status: Mapped[str] = mapped_column(String(32), default="pending")
    clinician_target_map: Mapped[float]

    device: Mapped[EdgeDevice] = relationship(back_populates="sessions")
