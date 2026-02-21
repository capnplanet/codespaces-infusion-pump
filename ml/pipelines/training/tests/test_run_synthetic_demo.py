from __future__ import annotations

import subprocess
from pathlib import Path

import yaml


def test_run_synthetic_demo_generates_artifacts(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    output_dir = tmp_path / "demo"

    subprocess.run(
        [
            "python",
            "run_synthetic_demo.py",
            "--output-dir",
            str(output_dir),
            "--sessions",
            "4",
            "--steps",
            "5",
            "--dataset-format",
            "csv",
        ],
        cwd=root,
        check=True,
    )

    dataset_path = output_dir / "data" / "synthetic_icustays.csv"
    fixture_path = output_dir / "fixtures" / "telemetry_stream.jsonl"
    config_path = output_dir / "configs" / "synthetic-baseline.yaml"

    assert dataset_path.exists()
    assert fixture_path.exists()
    assert config_path.exists()

    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert str(dataset_path) == config["dataset_path"]
