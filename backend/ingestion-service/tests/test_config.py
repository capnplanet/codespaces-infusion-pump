from __future__ import annotations

from ingestion_service.config import get_settings


def test_settings_defaults(monkeypatch) -> None:
    monkeypatch.delenv("INGESTION__KAFKA_TOPIC", raising=False)
    monkeypatch.delenv("INGESTION__KAFKA_SEND_MAX_RETRIES", raising=False)
    monkeypatch.delenv("INGESTION__IDEMPOTENCY_CACHE_SIZE", raising=False)
    monkeypatch.delenv("INGESTION__ENFORCE_DEVICE_API_KEYS", raising=False)
    monkeypatch.delenv("INGESTION__DEVICE_API_KEYS", raising=False)
    get_settings.cache_clear()  # type: ignore[attr-defined]

    settings = get_settings()

    assert settings.kafka_topic == "telemetry.events"
    assert settings.kafka_send_max_retries == 3
    assert settings.idempotency_cache_size == 10000
    assert settings.enforce_device_api_keys is True
    assert settings.device_api_keys == {}


def test_settings_override(monkeypatch) -> None:
    monkeypatch.setenv("INGESTION__KAFKA_TOPIC", "custom.topic")
    monkeypatch.setenv("INGESTION__KAFKA_SEND_MAX_RETRIES", "5")
    monkeypatch.setenv("INGESTION__KAFKA_SEND_BACKOFF_INITIAL_SECONDS", "0.2")
    monkeypatch.setenv("INGESTION__KAFKA_SEND_BACKOFF_MAX_SECONDS", "2.0")
    monkeypatch.setenv("INGESTION__IDEMPOTENCY_CACHE_SIZE", "500")
    monkeypatch.setenv("INGESTION__ENFORCE_DEVICE_API_KEYS", "false")
    monkeypatch.setenv("INGESTION__DEVICE_API_KEYS", '{"pump-01":"key-01"}')
    get_settings.cache_clear()  # type: ignore[attr-defined]

    settings = get_settings()

    assert settings.kafka_topic == "custom.topic"
    assert settings.kafka_send_max_retries == 5
    assert settings.kafka_send_backoff_initial_seconds == 0.2
    assert settings.kafka_send_backoff_max_seconds == 2.0
    assert settings.idempotency_cache_size == 500
    assert settings.enforce_device_api_keys is False
    assert settings.device_api_keys == {"pump-01": "key-01"}

    get_settings.cache_clear()  # type: ignore[attr-defined]
