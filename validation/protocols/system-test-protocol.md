# System Test Protocol

## Objective

Validate end-to-end behavior of the closed-loop infusion platform under nominal and fault conditions, ensuring requirements traceability to URS-FUNC-001..URS-FUNC-010 and risk controls.

## Pre-requisites

- Hardware-in-the-loop bench configured per `docs/architecture/system-architecture.md`.
- Firmware build ID recorded in configuration log.
- Edge gateway and backend services deployed in validation environment.

## Test Scenarios

1. **Nominal control loop**
   - Inject stable vitals, verify automated titration maintains MAP within ±5 mmHg of target.
2. **Sensor dropout**
   - Simulate missing MAP data; system must enter fallback within 2 control intervals.
3. **Low model confidence**
   - Force ML inference to report confidence <0.5; verify fallback and alarm activation.
4. **Clinician override**
   - Issue manual override; verify pump obeys manual rate and automation suspends.
5. **Cybersecurity event**
   - Attempt unauthorized configuration change; ensure access denied and audit log entry created.

## Documentation

Record results in the Validation Report template and link evidence files (telemetry logs, screenshots) with Part 11-compliant signatures.
