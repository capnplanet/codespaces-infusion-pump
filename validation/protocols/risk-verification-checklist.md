# Risk Control Verification Checklist

| Risk ID | Mitigation | Verification Method | Evidence Reference |
|---------|------------|---------------------|--------------------|
| RISK-001 | Firmware rate limiter | Unit test `firmware/tests/test_safety_controller.c` | Test report TR-001 |
| RISK-002 | Fallback protocol activation | System Test Scenario 2 | Validation report VR-002 |
| RISK-010 | ML confidence gating | Integration test `edge/inference-service/tests/test_service.py` | Validation report VR-006 |

Use this checklist during verification planning and update with results, deviations, and approvals.
