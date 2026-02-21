"""FastAPI service exposing local inference endpoint."""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, conlist

from .config import Settings, get_settings
from .model_runner import ModelRunner
from .telemetry_client import TelemetryClient

app = FastAPI(title="Edge Inference Service", version="0.1.0")


class InferenceRequest(BaseModel):
    features: Dict[str, conlist(float, min_length=1)]


class InferenceResponse(BaseModel):
    map_forecast: List[float]
    confidence: float
    metadata: Dict[str, float]


def _validate_features(features: Dict[str, List[float]], settings: Settings) -> None:
    if settings.required_feature_names:
        expected = set(settings.required_feature_names)
        provided = set(features.keys())
        if provided != expected:
            missing = sorted(expected - provided)
            extra = sorted(provided - expected)
            raise HTTPException(
                status_code=422,
                detail={"message": "Feature contract mismatch", "missing": missing, "extra": extra},
            )

    lengths = {len(values) for values in features.values()}
    if len(lengths) > 1:
        raise HTTPException(status_code=422, detail="All feature vectors must have equal length")


def _flatten_prediction(prediction: np.ndarray) -> List[float]:
    if prediction.ndim == 1:
        return prediction.astype(float).tolist()
    if prediction.ndim == 2 and prediction.shape[0] == 1:
        return prediction[0].astype(float).tolist()
    raise HTTPException(status_code=502, detail="Unexpected prediction shape")


def _extract_confidence(prediction: np.ndarray, metadata: Dict[str, Any], settings: Settings) -> float:
    raw_confidence = metadata.get("confidence")
    if raw_confidence is None and settings.allow_legacy_confidence_index:
        if prediction.ndim == 1 and prediction.size == 1:
            raw_confidence = float(prediction[0])
        elif prediction.ndim == 2 and prediction.shape[0] == 1 and prediction.shape[1] >= 2:
            raw_confidence = float(prediction[0][1])
        elif prediction.ndim == 2 and prediction.shape == (1, 1):
            raw_confidence = float(prediction[0][0])

    if raw_confidence is None:
        raise HTTPException(status_code=502, detail="Model output missing confidence value")

    try:
        confidence = float(raw_confidence)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="Model confidence is invalid") from exc

    if not np.isfinite(confidence) or confidence < 0.0 or confidence > 1.0:
        raise HTTPException(status_code=502, detail="Model confidence out of range")
    return confidence


def get_model_runner(settings: Settings = Depends(get_settings)) -> ModelRunner:
    return ModelRunner(
        model_path=str(settings.model_path),
        inference_timeout_ms=settings.inference_timeout_ms,
    )


def get_telemetry_client(settings: Settings = Depends(get_settings)) -> TelemetryClient:
    return TelemetryClient(
        transport=settings.telemetry_transport,
        endpoint=settings.telemetry_endpoint,
        grpc_target=settings.telemetry_grpc_target,
        api_key=settings.telemetry_api_key,
        default_session_id=settings.telemetry_session_id,
        default_device_id=settings.telemetry_device_id,
    )


@app.post("/predict", response_model=InferenceResponse)
def predict(
    request: InferenceRequest,
    runner: ModelRunner = Depends(get_model_runner),
    telem: TelemetryClient = Depends(get_telemetry_client),
    settings: Settings = Depends(get_settings),
) -> InferenceResponse:
    _validate_features(request.features, settings)

    try:
        prediction, metadata = runner.run(request.features)
    except RuntimeError as exc:  # deterministic fallback
        raise HTTPException(status_code=504, detail=str(exc)) from exc

    confidence = _extract_confidence(prediction, metadata, settings)
    if confidence < settings.min_confidence:
        raise HTTPException(status_code=409, detail="Confidence below threshold")

    map_forecast = _flatten_prediction(prediction)
    metadata["confidence"] = confidence
    telem.publish_prediction(prediction=map_forecast, metadata=metadata)
    return InferenceResponse(
        map_forecast=map_forecast,
        confidence=confidence,
        metadata={"inference_ms": metadata["inference_ms"]},
    )
