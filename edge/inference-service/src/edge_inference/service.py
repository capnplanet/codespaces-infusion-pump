"""FastAPI service exposing local inference endpoint."""

from __future__ import annotations

from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, conlist

from .config import Settings, get_settings
from .model_runner import ModelRunner
from .telemetry_client import TelemetryClient

app = FastAPI(title="Edge Inference Service", version="0.1.0")


class InferenceRequest(BaseModel):
    features: Dict[str, conlist(float, min_items=1)]


class InferenceResponse(BaseModel):
    map_forecast: List[float]
    confidence: float
    metadata: Dict[str, float]


def get_model_runner(settings: Settings = Depends(get_settings)) -> ModelRunner:
    return ModelRunner(
        model_path=str(settings.model_path),
        inference_timeout_ms=settings.inference_timeout_ms,
    )


def get_telemetry_client(settings: Settings = Depends(get_settings)) -> TelemetryClient:
    return TelemetryClient(settings.telemetry_endpoint, settings.telemetry_api_key)


@app.post("/predict", response_model=InferenceResponse)
def predict(
    request: InferenceRequest,
    runner: ModelRunner = Depends(get_model_runner),
    telem: TelemetryClient = Depends(get_telemetry_client),
    settings: Settings = Depends(get_settings),
) -> InferenceResponse:
    try:
        prediction, metadata = runner.run(request.features)
    except RuntimeError as exc:  # deterministic fallback
        raise HTTPException(status_code=504, detail=str(exc)) from exc

    confidence = float(prediction[0][1]) if prediction.ndim > 1 else float(prediction[0])
    if confidence < settings.min_confidence:
        raise HTTPException(status_code=409, detail="Confidence below threshold")

    telem.publish_prediction(prediction=prediction.tolist(), metadata=metadata)
    return InferenceResponse(
        map_forecast=prediction.tolist(),
        confidence=confidence,
        metadata={"inference_ms": metadata["inference_ms"]},
    )
