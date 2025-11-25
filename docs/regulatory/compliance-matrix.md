# Regulatory Alignment Matrix

This matrix maps repository assets and processes to key regulatory and standards expectations. It is intended to maximize alignment with FDA and international guidance; final conformity requires expert review and evidence.

| Guidance / Regulation | Relevant Requirements | Repository Artefacts & Activities |
|-----------------------|------------------------|-----------------------------------|
| FDA Infusion Pumps TPLC | Risk management, alarm validation, software verification | `docs/architecture/system-architecture.md`, `firmware/tests/`, `validation/protocols/` |
| FDA Device Software Functions (2023) | Software description, level of concern, requirements traceability | `docs/regulatory/software-description.md`, `docs/validation/traceability-matrix-template.xlsx`, `backend/api-service/app/schemas/` |
| FDA Cybersecurity Guidance | Threat modeling, SBOM, patching process, access control | `ops/security/threat-model.md`, `ops/security/sbom-template.cdx`, `docs/change-control/continuous-change-control-plan.md` |
| FDA AI-DSF Draft (2025) | PCCP, data management, algorithm change protocol | `docs/ml/ml-lifecycle.md`, `docs/change-control/ml-pccp.md`, `ml/pipelines/` |
| 21 CFR Part 11 | Audit trails, electronic signatures, system validation | `backend/api-service/app/models/audit.py`, `docs/validation/validation-master-plan.md`, `validation/` |
| 21 CFR 820 / ISO 13485 | Design controls, CAPA, DMR, DHF | `docs/validation/design-control-plan.md`, `docs/architecture/requirements-overview.md`, `docs/change-control/change-management-workflow.md` |
| ISO 14971 | Risk management lifecycle | `docs/regulatory/risk-management-plan.md`, `validation/protocols/risk-verification-checklist.md` |
| GAMP 5 | V-model, risk-based validation, supplier management | `docs/validation/validation-master-plan.md`, `validation/scripts/` |

## Next Steps

1. Populate each placeholder with organization-specific evidence and approvals.
2. Cross-reference QMS-controlled documents (URS, SDS, protocols) and ensure they are under document control.
3. Maintain the matrix as living document; update upon any regulatory guidance changes or significant system updates.
