"""Configuration management for the edge inference service."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from pydantic import BaseSettings, Field, PositiveInt


class Settings(BaseSettings):
    model_path: Path = Field(default=Path("/opt/edge/models/map_predictor.onnx"))
    inference_timeout_ms: PositiveInt = Field(default=150)
    min_confidence: float = Field(default=0.5)
    telemetry_endpoint: str = Field(default="http://localhost:8081/telemetry")
    telemetry_api_key: str = Field(default="change-me")
    host: str = Field(default="0.0.0.0")
    port: PositiveInt = Field(default=8080)

    class Config:
        env_prefix = "EDGE_INFER_"
        env_file = ".env"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
