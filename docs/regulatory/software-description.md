# Software Description

## Overview

The closed-loop vasopressor infusion platform comprises pump firmware, bedside gateway software, backend APIs, ML services, and user interfaces. This document summarizes the software functions, intended use, and architecture per FDA Device Software Functions guidance.

## Major Software Functions

1. **Dose Control Firmware (Class C)** — Enforces infusion limits, manages alarms, communicates with safety controller.
2. **Safety Controller Gateway (Class C)** — Aggregates patient data, executes deterministic control, supervises ML outputs.
3. **Edge ML Inference (Class B)** — Runs MAP prediction models locally with confidence gating.
4. **Backend Platform (Class B)** — Provides configuration management, audit trails, telemetry storage, clinician dashboards.
5. **ML Lifecycle Tooling (Class B)** — Supports data curation, model training, validation, and monitoring.

## Interfaces

- Fieldbus between pump and gateway (authenticated CAN-FD).
- gRPC telemetry ingestion between gateway and backend.
- REST APIs for configuration, overrides, and audit retrieval.
- FHIR/HL7 interfaces with hospital EHR systems.

## Operating Environment

- Embedded RTOS (QNX/Zephyr) on pump hardware.
- Hardened Linux with TPM on gateway.
- Kubernetes cluster for backend services.

## Assumptions

- Hospital IT provides network segmentation and PKI infrastructure.
- Clinical workflows include manual override capabilities.
