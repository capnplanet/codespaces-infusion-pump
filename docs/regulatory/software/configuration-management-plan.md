# Configuration Management Plan (CMP)

Document ID: SW-CMP
Version: 0.1 (Draft)
Effective Date: TBD
Owner: DevOps Lead
Approver: TBD
Change History: v0.1 Initial scaffold

## Scope
Defines configuration identification, control, status accounting, and audit for software baselines.

## Identification
- Repos, branches, tags; Docker images (name:tag@digest); artifacts (models, SBOMs).

## Control
- Change requests via PR with review; merge to protected `main` only after CI passes.
- Releases: semantic version tags; release notes `docs/regulatory/software/version-description-document.md`.

## Status Accounting
- Automated via CI; artifacts stored in registries with provenance.

## Audit
- Periodic configuration audits; traceability checks to requirements and risk controls.
