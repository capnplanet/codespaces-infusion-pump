"""Build synthetic data artifacts for an end-to-end demo pipeline."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import yaml

from synthetic_data import build_telemetry_fixture, generate_training_dataframe, write_training_dataset


def _load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _write_config(path: Path, config: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(config, handle, sort_keys=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("demo_artifacts"))
    parser.add_argument("--base-config", type=Path, default=Path("configs/baseline.yaml"))
    parser.add_argument("--sessions", type=int, default=60)
    parser.add_argument("--steps", type=int, default=24)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dataset-format", choices=["csv", "parquet"], default="csv")
    parser.add_argument("--run-training", action="store_true")
    parser.add_argument("--register-model", action="store_true")
    parser.add_argument("--registry-api-url", type=str, default="http://localhost:8000")
    parser.add_argument("--registry-id", type=str, default="map-predictor")
    parser.add_argument("--registry-version", type=str)
    parser.add_argument("--registry-token", type=str)
    parser.add_argument("--registry-jwt-secret", type=str)
    parser.add_argument("--registry-jwt-subject", type=str, default="dev-admin")
    parser.add_argument("--registry-jwt-roles", type=str, default="admin,clinician,auditor")
    args = parser.parse_args()

    output_dir = args.output_dir
    data_dir = output_dir / "data"
    config_dir = output_dir / "configs"
    fixture_dir = output_dir / "fixtures"

    dataset_path = data_dir / f"synthetic_icustays.{args.dataset_format}"
    fixture_path = fixture_dir / "telemetry_stream.jsonl"
    derived_config_path = config_dir / "synthetic-baseline.yaml"

    df = generate_training_dataframe(
        num_sessions=args.sessions,
        steps_per_session=args.steps,
        seed=args.seed,
    )
    write_training_dataset(df, dataset_path)
    build_telemetry_fixture(df, fixture_path)

    config = _load_config(args.base_config)
    config["dataset_path"] = str(dataset_path)
    _write_config(derived_config_path, config)

    print(f"Synthetic training dataset written: {dataset_path}")
    print(f"Synthetic telemetry fixture written: {fixture_path}")
    print(f"Derived training config written: {derived_config_path}")

    if args.run_training:
        train_cmd = ["python", "train.py", "--config", str(derived_config_path)]
        if args.register_model:
            train_cmd.extend(
                [
                    "--register-model",
                    "--registry-api-url",
                    args.registry_api_url,
                    "--registry-id",
                    args.registry_id,
                    "--registry-jwt-subject",
                    args.registry_jwt_subject,
                    "--registry-jwt-roles",
                    args.registry_jwt_roles,
                ]
            )
            if args.registry_version:
                train_cmd.extend(["--registry-version", args.registry_version])
            if args.registry_token:
                train_cmd.extend(["--registry-token", args.registry_token])
            if args.registry_jwt_secret:
                train_cmd.extend(["--registry-jwt-secret", args.registry_jwt_secret])

        subprocess.run(train_cmd, check=True)


if __name__ == "__main__":
    main()
