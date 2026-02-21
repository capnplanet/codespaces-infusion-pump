from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from synthetic_data import build_telemetry_fixture, generate_training_dataframe, write_training_dataset


def test_generate_training_dataframe_has_required_columns() -> None:
    df = generate_training_dataframe(num_sessions=4, steps_per_session=5, seed=7)

    required_columns = {
        "session_id",
        "device_id",
        "step",
        "map",
        "heart_rate",
        "spo2",
        "lactate",
        "creatinine",
        "age",
        "weight_kg",
        "hypotension_label",
    }

    assert required_columns.issubset(df.columns)
    assert len(df) == 20
    assert set(df["hypotension_label"].unique()).issubset({0, 1})
    assert df["hypotension_label"].nunique() == 2


def test_write_dataset_and_build_telemetry_fixture(tmp_path: Path) -> None:
    df = generate_training_dataframe(num_sessions=2, steps_per_session=3, seed=11)
    dataset_path = tmp_path / "synthetic.csv"
    fixture_path = tmp_path / "telemetry.jsonl"

    write_training_dataset(df, dataset_path)
    build_telemetry_fixture(df, fixture_path)

    reloaded = pd.read_csv(dataset_path)
    assert len(reloaded) == len(df)

    lines = fixture_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == len(df)

    event = json.loads(lines[0])
    assert {"session_id", "device_id", "sequence", "vitals", "pump_status", "predictions"}.issubset(event.keys())
    assert isinstance(event["vitals"], list)
    assert "confidence" in event["predictions"]
