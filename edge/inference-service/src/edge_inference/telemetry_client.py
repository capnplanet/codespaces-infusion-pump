"""Telemetry publisher sending predictions to backend."""

from __future__ import annotations

from typing import Any, Dict, List

import httpx


class TelemetryClient:
    """Simple HTTP client with API key header."""

    def __init__(self, endpoint: str, api_key: str) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._api_key = api_key

    def publish_prediction(self, prediction: List[float], metadata: Dict[str, Any]) -> None:
        payload = {"prediction": prediction, "metadata": metadata}
        headers = {"Authorization": f"Bearer {self._api_key}"}
        response = httpx.post(f"{self._endpoint}", json=payload, headers=headers, timeout=1.0)
        response.raise_for_status()
