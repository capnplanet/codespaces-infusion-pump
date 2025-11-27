# Threat Model Summary

| Asset | Threats | Mitigations |
|-------|---------|-------------|
| Pump firmware | Command spoofing, tampering | Secure boot, signed firmware, authenticated fieldbus, watchdog timers |
| Bedside gateway | Lateral movement, privilege escalation | SELinux policies, TPM-based attestation, minimal service exposure, segmented network |
| Backend APIs | Unauthorized configuration changes, data exfiltration | OIDC with MFA, RBAC, rate limiting, WAF, audit logging |
| Telemetry ingestion | Replay attacks, MITM | Mutual TLS, sequence counters, Kafka ACLs |
| ML pipeline | Data poisoning, shadow model drift | Dataset provenance checks, anomaly detection, dual approvals, reproducible builds |

## Next Actions

- Perform STRIDE analysis workshop with cybersecurity, QA/RA, and clinical teams.
- Update SBOM regularly and integrate with vulnerability management platform.
- Schedule penetration test prior to clinical pilot.
