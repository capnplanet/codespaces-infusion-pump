# Requirements Overview

This document enumerates high-level user and system requirements mapped to safety, performance, and regulatory needs. Detailed requirements reside within the organization's ALM tool; this summary supports design reviews and audits.

## User Requirements (URS)

- **URS-FUNC-001**: System shall maintain patient MAP within clinician-defined range.
- **URS-SAFE-002**: System shall prevent infusion rate from exceeding hard-coded maximum.
- **URS-SAFE-003**: System shall fall back to clinician-approved protocol when data quality is insufficient.
- **URS-INT-004**: System shall integrate with hospital EHR via FHIR APIs for patient context.
- **URS-CYBER-005**: System shall authenticate users via hospital SSO with MFA.

## System Requirements (SRS)

- **SRS-CTRL-001**: Safety controller shall update pump rate at 1 Hz with bounded rate-of-change.
- **SRS-CTRL-002**: Firmware shall enforce rate limits regardless of incoming commands.
- **SRS-ML-003**: ML inference shall provide confidence scores per prediction.
- **SRS-DATA-004**: Backend shall store telemetry with <1 second ingestion latency and immutable audit trail.
- **SRS-CYBER-005**: All communications shall use TLS 1.3 with mutual authentication where possible.

## Verification Strategy

Each requirement is linked to verification method (test, analysis, inspection) and associated protocol in `validation/protocols/`. Traceability maintained in ALM with references to this overview.
