# SBOM Process

Document ID: CYBER-SBOM
Version: 0.1 (Draft)
Effective Date: TBD
Owner: DevOps Lead
Approver: TBD
Change History: v0.1 Initial scaffold

## Scope
Define software bill of materials (SBOM) generation, storage, and delivery.

## Procedure
- Generate CycloneDX SBOMs during CI for each component.
- Store SBOMs as build artifacts and attach to releases; optionally publish to an SBOM registry.
- Provide SBOM to customers upon request and include in submission as needed.

## Linkage
- Integrates with vulnerability scans and release process.
