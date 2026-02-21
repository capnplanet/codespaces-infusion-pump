"""Configuration management for the edge inference service."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_path: Path = Field(default=Path("/opt/edge/models/map_predictor.onnx"))
    inference_timeout_ms: PositiveInt = Field(default=150)
    min_confidence: float = Field(default=0.5)
    required_feature_names: list[str] = Field(default_factory=list)
    allow_legacy_confidence_index: bool = Field(default=True)
    telemetry_transport: str = Field(default="http")
    telemetry_endpoint: str = Field(default="http://localhost:8081/telemetry")
    telemetry_grpc_target: str = Field(default="localhost:50051")
    telemetry_grpc_use_tls: bool = Field(default=False)
    telemetry_grpc_tls_ca_cert: Path | None = Field(default=None)
    telemetry_grpc_tls_client_cert: Path | None = Field(default=None)
    telemetry_grpc_tls_client_key: Path | None = Field(default=None)
    telemetry_session_id: str = Field(default="demo-session-000")
    telemetry_device_id: str = Field(default="pump-00")
    telemetry_api_key: str = Field(default="change-me")
    host: str = Field(default="0.0.0.0")
    port: PositiveInt = Field(default=8080)

    model_config = SettingsConfigDict(env_prefix="EDGE_INFER_", env_file=".env")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
