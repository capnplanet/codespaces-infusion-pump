"""Utility to assemble validation evidence packages."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

TEMPLATE = {
    "generated_at": None,
    "executed_by": None,
    "summary": None,
    "requirements": [],
    "test_cases": [],
}


def generate_report(output_path: Path, summary: str, executed_by: str, requirements: list[str], test_cases: list[dict]) -> None:
    data = TEMPLATE.copy()
    data.update(
        {
            "generated_at": datetime.utcnow().isoformat(),
            "executed_by": executed_by,
            "summary": summary,
            "requirements": requirements,
            "test_cases": test_cases,
        }
    )
    with output_path.open("w") as handle:
        yaml.safe_dump(data, handle)


if __name__ == "__main__":
    generate_report(
        Path("validation_report.yaml"),
        summary="Placeholder system test run",
        executed_by="qa.engineer@example.org",
        requirements=["URS-FUNC-001", "URS-SAFE-004"],
        test_cases=[{"id": "ST-001", "status": "PASS"}],
    )
