"""Baseline training pipeline for MAP prediction ensemble."""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, request

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
    model.fit(X_train.to_numpy(dtype=np.float32), y_train.to_numpy())
    return model


def export_xgboost_to_onnx(*, model: XGBClassifier, feature_names: list[str], output_path: Path) -> Path:
    try:
        from onnxmltools import convert_xgboost
        from onnxmltools.convert.common.data_types import FloatTensorType
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "ONNX export dependencies are missing. Install requirements.txt before running training."
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    initial_types = [("input", FloatTensorType([None, len(feature_names)]))]
    onnx_model = convert_xgboost(model, initial_types=initial_types, target_opset=15)
    with output_path.open("wb") as handle:
        handle.write(onnx_model.SerializeToString())
    return output_path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def build_deploy_artifact_bundle(
    *,
    run_id: str,
    model: XGBClassifier,
    feature_names: list[str],
    metrics: dict[str, Any],
    config: dict[str, Any],
    artifact_root: Path,
) -> dict[str, Any]:
    deploy_dir = artifact_root / "deploy"
    deploy_dir.mkdir(parents=True, exist_ok=True)

    model_path = export_xgboost_to_onnx(
        model=model,
        feature_names=feature_names,
        output_path=deploy_dir / "map_predictor.onnx",
    )

    acceptance = {
        "metrics": metrics,
        "thresholds": config.get("metrics", {}),
        "accepted": True,
    }
    acceptance_path = deploy_dir / "acceptance_summary.json"
    acceptance_path.write_text(json.dumps(acceptance, indent=2), encoding="utf-8")

    feature_contract = {
        "input_name": "input",
        "input_layout": "single_tensor_row_major",
        "dtype": "float32",
        "required_feature_names": feature_names,
        "required_feature_count": len(feature_names),
    }
    feature_contract_path = deploy_dir / "feature_contract.json"
    feature_contract_path.write_text(json.dumps(feature_contract, indent=2), encoding="utf-8")

    manifest = {
        "artifact_type": "deploy-ready-model-artifact",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "model_name": "map_predictor",
        "framework": "xgboost",
        "format": "onnx",
        "model_binary": {
            "path": model_path.name,
            "sha256": sha256_file(model_path),
            "size_bytes": model_path.stat().st_size,
        },
        "acceptance_summary": acceptance_path.name,
        "feature_contract": feature_contract_path.name,
        "inference_config": {
            "edge_infer_model_path": "/opt/edge/models/map_predictor.onnx",
            "required_feature_names": feature_names,
        },
    }
    manifest_path = deploy_dir / "deploy_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return {
        "deploy_dir": str(deploy_dir),
        "manifest_path": str(manifest_path),
        "model_binary_path": str(model_path),
        "model_sha256": manifest["model_binary"]["sha256"],
    }


def evaluate(model: XGBClassifier, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    preds = model.predict_proba(X_test.to_numpy(dtype=np.float32))[:, 1]
    auroc = roc_auc_score(y_test, preds)
    auprc = average_precision_score(y_test, preds)
    return {"auroc": float(auroc), "auprc": float(auprc)}


def check_acceptance(metrics: dict, thresholds: dict) -> None:
    if metrics["auroc"] < thresholds.get("auroc_threshold", 0.0):
        raise RuntimeError("Model AUROC below acceptance criterion")


def _base64url_json(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def build_dev_jwt(*, subject: str, roles: list[str], secret: str, ttl_minutes: int = 60) -> str:
    now = int(datetime.now(timezone.utc).timestamp())
    header = _base64url_json({"alg": "HS256", "typ": "JWT"})
    claims = _base64url_json({"sub": subject, "iat": now, "exp": now + (ttl_minutes * 60), "roles": roles})
    signing_input = f"{header}.{claims}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_part = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
    return f"{header}.{claims}.{signature_part}"


def register_model_version(
    *,
    registry_api_url: str,
    token: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    endpoint = registry_api_url.rstrip("/") + "/ml-models/"
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=10) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Model registry request failed ({exc.code}): {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Model registry request failed: {exc.reason}") from exc


def _is_registry_conflict(error_message: str) -> bool:
    lowered = error_message.lower()
    return "(409)" in lowered or "already exists" in lowered or "duplicate key" in lowered


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--skip-export", action="store_true")
    parser.add_argument("--register-model", action="store_true")
    parser.add_argument("--registry-api-url", default="http://localhost:8000")
    parser.add_argument("--registry-id", default="map-predictor")
    parser.add_argument("--registry-version", default=None)
    parser.add_argument("--registry-token", default=None)
    parser.add_argument("--registry-jwt-secret", default=None)
    parser.add_argument("--registry-jwt-subject", default="dev-admin")
    parser.add_argument("--registry-jwt-roles", default="admin,clinician,auditor")
    args = parser.parse_args()

    if args.register_model and args.skip_export:
        raise RuntimeError("--register-model requires deploy export. Remove --skip-export.")

    config = load_config(args.config)
    dataset = load_dataset(Path(config["dataset_path"]))
    X, y = build_features(dataset, config["features"])
    dataset_path = Path(config["dataset_path"])
    feature_names = [str(col) for col in X.columns]

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

        if not args.skip_export:
            deploy_bundle = build_deploy_artifact_bundle(
                run_id=run.info.run_id,
                model=model,
                feature_names=feature_names,
                metrics=metrics,
                config=config,
                artifact_root=artifact_dir,
            )
            deploy_summary_path = artifact_dir / "deploy_bundle.json"
            deploy_summary_path.write_text(json.dumps(deploy_bundle, indent=2), encoding="utf-8")
            mlflow.log_artifact(deploy_summary_path)
            mlflow.log_artifact(Path(deploy_bundle["manifest_path"]))
            mlflow.log_artifact(Path(deploy_bundle["model_binary_path"]))
            print(f"Deploy-ready artifact generated: {deploy_bundle['deploy_dir']}")

            if args.register_model:
                token = args.registry_token or os.getenv("MODEL_REGISTRY_TOKEN")
                if not token:
                    jwt_secret = args.registry_jwt_secret or os.getenv("MODEL_REGISTRY_JWT_SECRET")
                    if not jwt_secret:
                        raise RuntimeError(
                            "Model registration requires --registry-token or --registry-jwt-secret "
                            "(or MODEL_REGISTRY_TOKEN / MODEL_REGISTRY_JWT_SECRET)."
                        )
                    roles = [role.strip() for role in args.registry_jwt_roles.split(",") if role.strip()]
                    token = build_dev_jwt(
                        subject=args.registry_jwt_subject,
                        roles=roles,
                        secret=jwt_secret,
                    )

                registration_payload = {
                    "registry_id": args.registry_id,
                    "version": args.registry_version or run.info.run_id,
                    "dataset_hash": sha256_file(dataset_path),
                    "validation_report_path": deploy_bundle["manifest_path"],
                    "acceptance_summary": {
                        "metrics": metrics,
                        "artifact_bundle": deploy_bundle,
                    },
                }

                try:
                    registered = register_model_version(
                        registry_api_url=args.registry_api_url,
                        token=token,
                        payload=registration_payload,
                    )
                except RuntimeError as exc:
                    if not _is_registry_conflict(str(exc)):
                        raise

                    fallback_registry_id = f"{args.registry_id}-{run.info.run_id[:12]}"
                    registration_payload["registry_id"] = fallback_registry_id
                    registered = register_model_version(
                        registry_api_url=args.registry_api_url,
                        token=token,
                        payload=registration_payload,
                    )
                    print(
                        "Model registry_id conflict detected; retried with run-scoped registry_id: "
                        f"{fallback_registry_id}"
                    )

                registration_path = artifact_dir / "model_registry_registration.json"
                registration_path.write_text(json.dumps(registered, indent=2), encoding="utf-8")
                mlflow.log_artifact(registration_path)
                print(
                    "Model registered in API: "
                    f"id={registered.get('id')} registry_id={registered.get('registry_id')} version={registered.get('version')}"
                )


if __name__ == "__main__":
    main()
