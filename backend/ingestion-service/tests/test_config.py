def test_settings_override(monkeypatch):
from ingestion_service.config import Settings, get_settings


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("INGESTION__KAFKA_TOPIC", raising=False)
    get_settings.cache_clear()  # type: ignore[attr-defined]
    settings = get_settings()
    assert settings.kafka_topic == "telemetry.events"


def test_settings_override(monkeypatch):
    monkeypatch.setenv("INGESTION__KAFKA_TOPIC", "custom.topic")
    get_settings.cache_clear()  # type: ignore[attr-defined]
    settings = get_settings()
    assert settings.kafka_topic == "custom.topic"
    get_settings.cache_clear()  # type: ignore[attr-defined]
