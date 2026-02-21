"""Synchronize technical debt records with anomaly and traceability control artifacts."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class DebtItem:
    debt_id: str
    component: str
    description: str
    severity: str
    status: str
    evidence_link: str


def _extract_table_rows(markdown_text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        if set(stripped.replace("|", "").replace("-", "").replace(" ", "")) == set():
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        rows.append(cells)
    return rows


def parse_debt_register(path: Path) -> list[DebtItem]:
    text = path.read_text(encoding="utf-8")
    rows = _extract_table_rows(text)
    debt_items: list[DebtItem] = []

    for row in rows:
        if not row or not row[0].startswith("TD-"):
            continue
        if len(row) < 9:
            continue
        debt_items.append(
            DebtItem(
                debt_id=row[0],
                component=row[1],
                description=row[2],
                severity=row[3],
                status=row[6],
                evidence_link=row[8],
            )
        )

    return debt_items


def update_problem_anomaly_log(par_path: Path, debt_items: list[DebtItem]) -> None:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    header = """# Problem/Anomaly Report Log

Document ID: SW-PAR
Version: 0.2
Effective Date: {effective_date}
Owner: QA/RA
Approver: QA/RA Delegate
Change History: v0.2 Auto-synced from technical debt register

Record discovered defects, anomalies, and resolutions; link to trackers and test evidence.

| ID | Title | Component | Severity | Status | Discovered In | Resolved In | Link |
|---|---|---|---|---|---|---|---|
""".format(effective_date=generated_at)

    lines = [header]
    for index, item in enumerate(debt_items, start=1):
        resolved_in = "Evidence linked in debt register" if item.status.lower() == "closed" else ""
        lines.append(
            "| {id_num:03d} | {title} | {component} | {severity} | {status} | {discovered} | {resolved} | {link} |\n".format(
                id_num=index,
                title=item.debt_id,
                component=item.component,
                severity=item.severity,
                status=item.status,
                discovered="docs/change-control/technical-debt-register.md",
                resolved=resolved_in,
                link=item.evidence_link,
            )
        )

    par_path.write_text("".join(lines) + "\n", encoding="utf-8")


def generate_traceability_gap_report(traceability_csv: Path, debt_items: list[DebtItem], output_path: Path) -> None:
    with traceability_csv.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    tbd_rows: list[dict[str, str]] = []
    for row in rows:
        if any("tbd" in (value or "").lower() for value in row.values()):
            tbd_rows.append(row)

    report_lines = [
        "# Debt and Traceability Gap Report\n\n",
        f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n",
        "## Open Debt Items\n\n",
    ]

    open_items = [item for item in debt_items if item.status.lower() != "closed"]
    if open_items:
        for item in open_items:
            report_lines.append(
                f"- {item.debt_id}: {item.description} (Severity: {item.severity}, Status: {item.status}, Evidence: {item.evidence_link})\n"
            )
    else:
        report_lines.append("- None\n")

    report_lines.append("\n## Traceability Rows With TBD\n\n")
    if tbd_rows:
        for row in tbd_rows:
            report_lines.append(
                "- {req}: Verification Artifact='{artifact}', Risk ID='{risk}'\n".format(
                    req=row.get("Requirement ID", ""),
                    artifact=row.get("Verification Artifact", ""),
                    risk=row.get("Risk ID", ""),
                )
            )
    else:
        report_lines.append("- None\n")

    output_path.write_text("".join(report_lines), encoding="utf-8")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    debt_register = repo_root / "docs/change-control/technical-debt-register.md"
    problem_anomaly_log = repo_root / "docs/regulatory/software/problem-anomaly-report.md"
    traceability_csv = repo_root / "docs/validation/traceability-matrix-template.csv"
    gap_report = repo_root / "validation/reports/debt-traceability-gap-report.md"

    debt_items = parse_debt_register(debt_register)
    update_problem_anomaly_log(problem_anomaly_log, debt_items)
    generate_traceability_gap_report(traceability_csv, debt_items, gap_report)


if __name__ == "__main__":
    main()
