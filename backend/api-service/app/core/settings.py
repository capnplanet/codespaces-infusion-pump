"""Application configuration using pydantic settings."""

from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """Runtime configuration for the API service."""

    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    telemetry_topic: str = "telemetry.events"
    audit_topic: str = "audit.events"

    model_config = SettingsConfigDict(env_prefix="API_SETTINGS__", env_file=".env")


@lru_cache(maxsize=1)
def get_settings() -> APISettings:
    return APISettings()
