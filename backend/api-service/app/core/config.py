"""Application configuration settings."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Infusion Platform API"
    database_url: str
    telemetry_topic: str = "telemetry.pump"
    auth_oidc_issuer: str = "https://idp.example.com"
    auth_client_id: str = "infusion-platform"
    allowed_origins: List[str] = ["https://infusion.examplehospital.org"]
    audit_log_retention_days: int = 3650

    model_config = SettingsConfigDict(env_prefix="API_SETTINGS__")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]
