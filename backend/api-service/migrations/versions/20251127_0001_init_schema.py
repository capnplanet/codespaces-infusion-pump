"""Initial schema derived from domain models.

Revision ID: 20251127_0001
Revises: 
Create Date: 2025-11-27
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20251127_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("mrn", sa.String(length=64), nullable=False),
        sa.Column("hashed_mrn", sa.String(length=128), nullable=False),
        sa.Column("demographics", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_by", sa.String(length=128), nullable=True),
        sa.UniqueConstraint("mrn"),
        sa.UniqueConstraint("hashed_mrn"),
    )
    op.create_index("ix_patients_mrn", "patients", ["mrn"], unique=False)

    op.create_table(
        "device_configurations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("device_id", sa.String(length=64), nullable=False),
        sa.Column("firmware_version", sa.String(length=32), nullable=False),
        sa.Column("gateway_version", sa.String(length=32), nullable=False),
        sa.Column("config_payload", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_by", sa.String(length=128), nullable=True),
        sa.UniqueConstraint("device_id"),
    )
    op.create_index("ix_device_configurations_device_id", "device_configurations", ["device_id"], unique=False)

    op.create_table(
        "drug_library_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("drug_name", sa.String(length=64), nullable=False),
        sa.Column("concentration_mcg_per_ml", sa.Float(), nullable=False),
        sa.Column("min_rate_mcg_per_kg_min", sa.Float(), nullable=False),
        sa.Column("max_rate_mcg_per_kg_min", sa.Float(), nullable=False),
        sa.Column("max_delta_mcg_per_kg_min", sa.Float(), nullable=False),
        sa.Column("safety_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_by", sa.String(length=128), nullable=True),
    )
    op.create_index("ix_drug_library_entries_drug_name", "drug_library_entries", ["drug_name"], unique=False)

    op.create_table(
        "pump_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("device_configuration_id", sa.Integer(), nullable=False),
        sa.Column("clinician_target_map_mmhg", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_by", sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["device_configuration_id"], ["device_configurations.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "control_parameters",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_by", sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["pump_sessions.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "ml_model_versions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("registry_id", sa.String(length=128), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("dataset_hash", sa.String(length=128), nullable=False),
        sa.Column("validation_report_path", sa.String(length=256), nullable=False),
        sa.Column("acceptance_summary", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_by", sa.String(length=128), nullable=True),
        sa.UniqueConstraint("registry_id"),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actor", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("resource", sa.String(length=256), nullable=False),
        sa.Column("before", postgresql.JSONB(), nullable=True),
        sa.Column("after", postgresql.JSONB(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("ml_model_versions")
    op.drop_table("control_parameters")
    op.drop_table("pump_sessions")
    op.drop_table("drug_library_entries")
    op.drop_table("device_configurations")
    op.drop_index("ix_patients_mrn", table_name="patients")
    op.drop_table("patients")
