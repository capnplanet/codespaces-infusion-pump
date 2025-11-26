"""Control configuration models."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import AuditMixin, Base


class DrugLibrary(Base, AuditMixin):
    __tablename__ = "drug_libraries"

    name: Mapped[str] = mapped_column(String(64), unique=True)
    version: Mapped[str] = mapped_column(String(32))
    payload: Mapped[dict] = mapped_column(JSONB)


class ControlParameterSet(Base, AuditMixin):
    __tablename__ = "control_parameter_sets"

    drug_library_id: Mapped[int] = mapped_column(ForeignKey("drug_libraries.id"))
    label: Mapped[str] = mapped_column(String(64))
    limits: Mapped[dict] = mapped_column(JSONB)  # min/max dose, ramp limits
