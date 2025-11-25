# System Architecture Overview

This document captures the implementation-ready architecture for the closed-loop vasopressor infusion platform. It is intended to maximize alignment with FDA Infusion Pump TPLC guidance, Content of Premarket Submissions for Device Software Functions (2023), Cybersecurity in Medical Devices, and the 2025 draft AI-DSF guidance. Final approval depends on detailed evidence, clinical validation, and regulator review.

## Component Summary

| Layer | Technology | Responsibility | Safety Classification |
|-------|------------|----------------|------------------------|
| Pump Firmware | C/C++ on QNX or Zephyr RTOS | Motor control, dose enforcement, primary alarms, secure comms | Class C (safety critical) |
| Bedside Gateway | Rust safety controller, Python inference, hardened Linux | Aggregate vitals, run deterministic safety controller, execute ML inference, buffer logs | Class C safety controller; supporting services Class B |
| Backend Platform | FastAPI microservices, PostgreSQL/TimescaleDB, Kafka | Configuration, telemetry ingestion, audit trails, clinician dashboards, device fleet management | Mixed (safety support + business) |
| ML Services | MLflow/Kubeflow, Delta Lake, XGBoost + TCN ensemble | Data governance, model training, validation, registry, deployment | Class B supporting |
| Web Portals | React/TypeScript | Clinician monitoring, QA/RA evidence, biomedical engineering tools | Class A (non-safety) |

## Trust Boundaries

1. **Safety-Critical Domain**: Pump firmware and gateway safety controller communicate over authenticated fieldbus (CANopen/CAN-FD). All commands cryptographically signed. Network isolated via VLAN and hardware firewalls.
2. **Clinical Network Domain**: Backend services reside in segmented hospital data center with zero-trust policies, mutual TLS enforced, strict RBAC using OIDC.
3. **Analytics Domain**: ML training environments and analytics dashboards separated from production by data diode or read-only replication. No direct control messages permitted.
4. **Maintenance Domain**: OTA updates delivered from signed artifact repository via secure update service; requires dual approval (engineering + QA/RA) and cryptographic attestation.

## Data Flows

- Real-time vitals and pump telemetry stream from gateway → backend ingestion service via gRPC/TLS 1.3 (mutual auth). Messages serialized with Protocol Buffers and include sequence counters and HMAC.
- Configuration commands flow backend → gateway after RBAC check, change-control approval, and dual confirmation when altering safety parameters.
- ML inference inputs originate locally on gateway; only metadata and predictions forwarded to backend for audit and monitoring.
- EHR integration via FHIR R4 (SMART-on-FHIR) for demographics and lab data, with caching in backend for session initialization.

## Safety Logic Segregation

- Safety controller binary (Rust) runs under high-reliability supervisor on gateway, isolated from non-critical containers via SELinux and seccomp.
- Firmware enforces non-bypassable ceilings/minimums and rate-of-change limits regardless of incoming commands.
- If gateway detects missing data, low model confidence, or internal anomaly, it commands firmware to revert to clinician-approved fallback profile and raises alarm.

## Deployment Topology

- Minimum configuration: redundant gateways per patient (active/standby) with automatic failover, backend deployed on highly available Kubernetes cluster (3 control planes, ≥2 worker nodes), PostgreSQL in streaming replication, Kafka cluster with 3 brokers.
- Observability stack (Prometheus, Grafana, Loki) collects metrics/logs. Alerts integrated into hospital SOC for cybersecurity events.

## External Interfaces

- Bedside monitor integration: HL7 v2 or vendor APIs bridging into gateway via interface engine (e.g., Mirth) with deterministic latency budget (<500 ms).
- Pump hardware abstraction defined in `firmware/include/pump_hal.h`; hardware-in-the-loop bench replicates sensors and occlusions for verification.
- Clinician portal accessible only through hospital intranet with MFA; overrides require human presence confirmation and leave Part 11-compliant audit trail.

## Assumptions to Validate

- Hospital IT can provide segregated VLANs and 802.1X for edge devices.
- EHR vendor supports required FHIR endpoints with appropriate refresh tokens.
- Clinical leadership approves fallback dosing tables and override procedures.
- QMS tooling (e.g., Polarion, MasterControl) available for requirements and document control integration.
