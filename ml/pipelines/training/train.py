"""Baseline training pipeline for MAP prediction ensemble."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


def load_config(path: Path) -> dict:
    with path.open() as fh:
        return yaml.safe_load(fh)


def load_dataset(dataset_path: Path) -> pd.DataFrame:
    if dataset_path.suffix == ".parquet":
        return pd.read_parquet(dataset_path)
    if dataset_path.suffix == ".csv":
        return pd.read_csv(dataset_path)
    raise ValueError(f"Unsupported dataset extension: {dataset_path.suffix}")


def build_features(df: pd.DataFrame, feature_config: dict) -> tuple[pd.DataFrame, pd.Series]:
    feature_columns = feature_config["vital_signs"] + feature_config.get("labs", []) + feature_config.get("demographics", [])
    X = df[feature_columns].fillna(method="ffill").fillna(method="bfill")
    y = df["hypotension_label"]
    return X, y


def train_xgboost(X_train: pd.DataFrame, y_train: pd.Series, params: dict) -> XGBClassifier:
    model = XGBClassifier(
        max_depth=params.get("max_depth", 4),
        learning_rate=params.get("learning_rate", 0.05),
        n_estimators=params.get("n_estimators", 300),
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="auc",
    )
    model.fit(X_train, y_train)
    return model


def evaluate(model: XGBClassifier, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    preds = model.predict_proba(X_test)[:, 1]
    auroc = roc_auc_score(y_test, preds)
    auprc = average_precision_score(y_test, preds)
    return {"auroc": float(auroc), "auprc": float(auprc)}


def check_acceptance(metrics: dict, thresholds: dict) -> None:
    if metrics["auroc"] < thresholds.get("auroc_threshold", 0.0):
        raise RuntimeError("Model AUROC below acceptance criterion")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    config = load_config(args.config)
    dataset = load_dataset(Path(config["dataset_path"]))
    X, y = build_features(dataset, config["features"])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    mlflow.set_experiment(config["experiment_name"])
    with mlflow.start_run() as run:
        model = train_xgboost(X_train, y_train, config["model"]["xgboost"])
        metrics = evaluate(model, X_test, y_test)
        check_acceptance(metrics, config.get("metrics", {}))

        mlflow.log_params(config["model"]["xgboost"])
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, "map_predictor")

        artifact_dir = Path("artifacts") / run.info.run_id
        artifact_dir.mkdir(parents=True, exist_ok=True)
        summary_path = artifact_dir / "metrics.json"
        summary_path.write_text(json.dumps(metrics, indent=2))
        mlflow.log_artifact(summary_path)


if __name__ == "__main__":
    main()
