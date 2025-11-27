# Cybersecurity Plan — Premarket Submission Content

Document ID: CYBER-PLAN
Version: 0.1 (Draft)
Effective Date: TBD
Owner: Security Lead
Approver: TBD
Change History: v0.1 Initial scaffold

## Guidance Basis
- FDA Cybersecurity in Medical Devices — Quality System Considerations and Content of Premarket Submissions (2023)

## Threat Modeling and Risk Assessment
- See `ops/security/threat-model.md` and `docs/regulatory/risk/hazard-analysis.md`.

## Design Controls
- Secure communications (mTLS) between all services
- AuthZ/AuthN (OIDC/JWT) for APIs
- Least privilege; network segmentation; logging and audit trails

## SBOM and Vulnerability Management
- SBOM: CycloneDX generation in CI; see `docs/regulatory/cybersecurity/sbom-process.md`
- Vulnerability scanning: dependency audits (pip/audit, cargo-audit), container scanning

## Cryptography and Key Management
- Certificate provisioning for devices; secrets handling via Kubernetes Secrets/External Secrets (TBD)

## Patching and Updates
- Container image rebuilds and rollouts; firmware secure update

## Postmarket Surveillance
- Vulnerability intake and coordinated disclosure process (TBD)
