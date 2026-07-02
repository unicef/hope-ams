import json
import logging
from abc import abstractmethod
from typing import Any

from hope_ams.ai import (
    AIServiceError,
    OllamaClient,
    OllamaResponseError,
)
from hope_ams.detection.rules.base import BaseRule, Finding, RuleContext

logger = logging.getLogger(__name__)


class BaseLLMRule(BaseRule):
    system_prompt: str = ""
    ollama_model: str | None = None
    use_json_format: bool = True
    default_config: dict[str, Any] = {
        "fail_open": True,
    }

    @abstractmethod
    def build_prompt(self, ctx: RuleContext) -> str: ...

    def parse_response(self, response: str) -> list[Finding]:
        data = json.loads(response)
        if isinstance(data, list):
            return [Finding(**item) for item in data]
        if isinstance(data, dict):
            items = data.get("findings", data.get("results", [data]))
            if isinstance(items, list):
                return [Finding(**item) for item in items]
            return [Finding(**data)]
        msg = f"Unexpected LLM response type: {type(data).__name__}"
        raise OllamaResponseError(msg)

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        config = self.get_config(ctx)
        fail_open = config.get("fail_open", True)
        model = config.get("ollama_model") or self.ollama_model
        system = config.get("system_prompt") or self.system_prompt

        prompt = self.build_prompt(ctx)

        client = OllamaClient()
        if not client.enabled:
            if fail_open:
                logger.debug("LLM rule %s skipped: Ollama not configured", self.name)
                return []
            msg = "Ollama is not configured (set OLLAMA_BASE_URL)"
            from hope_ams.ai.exceptions import OllamaConnectionError

            raise OllamaConnectionError(msg)

        try:
            response = client.generate(
                prompt=prompt,
                system_prompt=system or None,
                model=model or None,
                response_format="json" if self.use_json_format else None,
            )
        except AIServiceError:
            logger.warning("LLM rule %s failed", self.name, exc_info=True)
            if fail_open:
                return []
            raise

        try:
            return self.parse_response(response)
        except (json.JSONDecodeError, OllamaResponseError, TypeError, KeyError) as e:
            logger.warning("LLM rule %s: failed to parse response: %s", self.name, e)
            if fail_open:
                return []
            raise
