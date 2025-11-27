-- Migration: Create core regulated tables
-- Note: execute via Alembic or controlled DBA change procedure

CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    mrn VARCHAR(64) UNIQUE NOT NULL,
    hashed_mrn VARCHAR(128) UNIQUE NOT NULL,
    demographics JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by VARCHAR(128) NOT NULL,
    modified_at TIMESTAMPTZ,
    modified_by VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS device_configurations (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(64) UNIQUE NOT NULL,
    firmware_version VARCHAR(32) NOT NULL,
    gateway_version VARCHAR(32) NOT NULL,
    config_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by VARCHAR(128) NOT NULL,
    modified_at TIMESTAMPTZ,
    modified_by VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS pump_sessions (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    device_configuration_id INTEGER NOT NULL REFERENCES device_configurations(id),
    clinician_target_map_mmhg DOUBLE PRECISION NOT NULL,
    status VARCHAR(32) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by VARCHAR(128) NOT NULL,
    modified_at TIMESTAMPTZ,
    modified_by VARCHAR(128)
);
