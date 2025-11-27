# SOUP Inventory (Software of Unknown Provenance)

Document ID: SW-SOUP
Version: 0.1 (Draft)
Effective Date: TBD
Owner: Software Lead
Approver: TBD
Change History: v0.1 Initial scaffold

List third-party software, versions, licenses, intended use, and safety impact. Keep synchronized with SBOM.

| Component | Version | License | Location | Intended Use | Safety Impact | Controls |
|---|---:|---|---|---|---|---|
| Python (FastAPI, SQLAlchemy, aiokafka, grpcio, onnxruntime, etc.) | TBD | Various | `edge/`, `backend/` | Services and ML inference | Medium | Pin versions, tests, SBOM, vulnerability scans |
| Rust crates (tokio, serde, etc.) | TBD | Various | `edge/safety-controller` | Safety controller | High | Cargo audit, tests |
| C/C++ libs (if any) | TBD | Various | `firmware/` | Firmware support | High | Static analysis, code review |

Maintain authoritative list via dependency lockfiles and CI SBOM generation.
