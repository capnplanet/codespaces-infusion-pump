# Hazard Analysis

Document ID: RISK-HAZARD
Version: 0.1 (Draft)
Effective Date: TBD
Owner: Risk Manager
Approver: TBD
Change History: v0.1 Initial scaffold

Refer to ISO 14971:2019. Link each hazard to risk controls and verification.

| Hazard | Sequence of Events | Harm | Initial Risk | Risk Controls | Residual Risk | Verification |
|---|---|---|---|---|---|---|
| Over-infusion due to ML misprediction | Sensor noise → model error → high dose | Hypotension/arrhythmia | High | Confidence gating; safety controller clamp; alarms | TBD | Unit/integration tests; HIL |
| Loss of communication | Link failure → stale command | Hemodynamic instability | High | Watchdog fallback; last-known-safe dose | TBD | Fault injection |
