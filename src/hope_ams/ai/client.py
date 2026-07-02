import json
import logging
from typing import Any

import requests
from django.conf import settings
from requests.exceptions import (
    ConnectionError as RequestsConnectionError,
    Timeout as RequestsTimeout,
)

from .exceptions import (
    OllamaConnectionError,
    OllamaResponseError,
    OllamaTimeoutError,
)

logger = logging.getLogger(__name__)

OLLAMA_GENERATE_URL = "/api/generate"
OLLAMA_TAGS_URL = "/api/tags"


class OllamaClient:
    def __init__(
        self,
        base_url: str | None = None,
        default_model: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self.base_url = (base_url or self._get_setting("OLLAMA_BASE_URL", "")).rstrip("/")
        self.default_model = default_model or self._get_setting("OLLAMA_DEFAULT_MODEL", "llama3")
        self.timeout = timeout or self._get_setting("OLLAMA_TIMEOUT", 120)

    @staticmethod
    def _get_setting(name: str, default: Any) -> Any:
        return getattr(settings, name, default) if hasattr(settings, name) else default

    @property
    def enabled(self) -> bool:
        return bool(self.base_url)

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        response_format: str | None = None,
    ) -> str:
        if not self.enabled:
            msg = "Ollama is not configured (OLLAMA_BASE_URL is empty)"
            raise OllamaConnectionError(msg)

        url = f"{self.base_url}{OLLAMA_GENERATE_URL}"
        payload: dict[str, Any] = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt
        if response_format:
            payload["format"] = response_format

        logger.debug("Ollama generate: model=%s url=%s", payload["model"], url)

        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
        except RequestsConnectionError as e:
            msg = f"Could not connect to Ollama at {url}: {e}"
            raise OllamaConnectionError(msg) from e
        except RequestsTimeout as e:
            msg = f"Ollama request timed out after {self.timeout}s"
            raise OllamaTimeoutError(msg) from e

        if resp.status_code != 200:
            msg = f"Ollama returned HTTP {resp.status_code}: {resp.text[:500]}"
            raise OllamaResponseError(msg)

        try:
            data: dict[str, Any] = resp.json()
        except json.JSONDecodeError as e:
            msg = f"Ollama returned non-JSON response: {resp.text[:500]}"
            raise OllamaResponseError(msg) from e

        response_text = str(data.get("response", ""))
        if not response_text:
            msg = "Ollama response is missing 'response' field"
            raise OllamaResponseError(msg)

        return response_text

    def is_available(self) -> bool:
        if not self.enabled:
            return False
        url = f"{self.base_url}{OLLAMA_TAGS_URL}"
        try:
            resp = requests.get(url, timeout=5)
        except requests.RequestException:
            return False
        else:
            return resp.status_code == 200
