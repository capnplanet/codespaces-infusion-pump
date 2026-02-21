"""Synthetic data utilities for demo training and telemetry fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


def generate_training_dataframe(
    *,
    num_sessions: int = 50,
    steps_per_session: int = 24,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows: list[dict] = []

    for session_index in range(num_sessions):
        session_id = f"demo-session-{session_index:03d}"
        device_id = f"pump-{session_index % 8:02d}"
        baseline_map = rng.normal(72.0, 6.0)
        age = float(np.clip(rng.normal(64.0, 12.0), 18.0, 95.0))
        weight_kg = float(np.clip(rng.normal(78.0, 15.0), 40.0, 160.0))

        for step in range(steps_per_session):
            hypotension_shift = rng.normal(0.0, 5.0)
            map_value = float(np.clip(baseline_map + hypotension_shift, 45.0, 110.0))
            heart_rate = float(np.clip(92.0 - (map_value - 65.0) * 0.8 + rng.normal(0.0, 6.0), 45.0, 180.0))
            spo2 = float(np.clip(97.0 - max(0.0, 62.0 - map_value) * 0.2 + rng.normal(0.0, 1.0), 80.0, 100.0))
            lactate = float(np.clip(1.6 + max(0.0, 65.0 - map_value) * 0.07 + rng.normal(0.0, 0.15), 0.4, 8.0))
            creatinine = float(np.clip(0.9 + rng.normal(0.0, 0.2), 0.4, 3.0))
            risk_score = (
                0.08 * (65.0 - map_value)
                + 0.02 * (heart_rate - 85.0)
                + 0.3 * (lactate - 1.8)
                + rng.normal(0.0, 0.25)
            )
            hypotension_label = int(risk_score > 0.0)

            rows.append(
                {
                    "session_id": session_id,
                    "device_id": device_id,
                    "step": step,
                    "map": map_value,
                    "heart_rate": heart_rate,
                    "spo2": spo2,
                    "lactate": lactate,
                    "creatinine": creatinine,
                    "age": age,
                    "weight_kg": weight_kg,
                    "hypotension_label": hypotension_label,
                }
            )

    return pd.DataFrame(rows)


def write_training_dataset(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix == ".parquet":
        df.to_parquet(output_path, index=False)
        return
    if output_path.suffix == ".csv":
        df.to_csv(output_path, index=False)
        return
    raise ValueError(f"Unsupported output extension: {output_path.suffix}")


def build_telemetry_fixture(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sorted_df = df.sort_values(["session_id", "step"]).reset_index(drop=True)
    sequence_by_session: dict[str, int] = {}

    with output_path.open("w", encoding="utf-8") as handle:
        for row in sorted_df.itertuples(index=False):
            sequence = sequence_by_session.get(row.session_id, 0) + 1
            sequence_by_session[row.session_id] = sequence

            confidence = float(np.clip(0.6 + abs(65.0 - row.map) * 0.01, 0.55, 0.98))
            event = {
                "session_id": row.session_id,
                "device_id": row.device_id,
                "sequence": sequence,
                "vitals": [
                    {"name": "map", "value": row.map, "timestamp_ms": int(row.step * 60_000)},
                    {"name": "heart_rate", "value": row.heart_rate, "timestamp_ms": int(row.step * 60_000)},
                    {"name": "spo2", "value": row.spo2, "timestamp_ms": int(row.step * 60_000)},
                ],
                "pump_status": {
                    "rate_mcg_per_kg_min": float(np.clip(0.06 + (65.0 - row.map) * 0.003, 0.02, 0.9)),
                    "fallback_active": confidence < 0.7,
                    "alarm_triggered": row.map < 55.0,
                },
                "predictions": {
                    "hypotension_risk": float(row.hypotension_label),
                    "confidence": confidence,
                },
            }
            handle.write(json.dumps(event) + "\n")
