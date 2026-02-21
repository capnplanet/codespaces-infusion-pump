# Gateway Bootstrap Procedure

1. **Provision Hardware**
   - Confirm serial numbers logged in asset management system.
   - Install hardened Linux image with SELinux enforcing and secure boot enabled.

2. **Load Credentials**
   - Inject TPM-backed device certificate signed by hospital PKI.
   - Store API bootstrap token securely (one-time use).

3. **Install Software Bundle**
   - Deploy container runtime (Balena/K3s) per cybersecurity hardening guide.
   - Install Rust safety controller and Python inference container images (signed with in-toto attestations).

4. **Run Self-Test**
   - Execute `ops/iot/scripts/gateway_self_test.sh` to validate container runtime, cert material, and secure ingestion/API reachability.
   - The self-test validates both mTLS channel readiness and ingestion API-key enforcement (`pump-00` dev credential).
   - Optional: set `STACK_FILE` to point at a non-default compose file.
   - Capture `ops/iot/self-test-logs/gateway-self-test-*.log` and upload to eQMS.

5. **Commission Device**
   - Register device using backend API `POST /devices/configurations`.
   - Apply clinician-approved dosing library.
   - Document completion with Part 11-compliant signature.
