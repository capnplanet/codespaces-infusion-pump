"""Configuration management for telemetry ingestion service."""

from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "telemetry.events"
    kafka_send_max_retries: int = 3
    kafka_send_backoff_initial_seconds: float = 0.1
    kafka_send_backoff_max_seconds: float = 1.0
    idempotency_cache_size: int = 10000
    enforce_device_api_keys: bool = True
    device_api_keys: dict[str, str] = {}
    audit_endpoint: str = "http://api:8000/audit/events"
    audit_api_token: str = "change-me"
    tls_cert_path: str = "/etc/infusion/certs/server.crt"
    tls_key_path: str = "/etc/infusion/certs/server.key"
    tls_ca_path: str = "/etc/infusion/certs/ca.crt"

    model_config = SettingsConfigDict(env_prefix="INGESTION__", env_file=".env")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
