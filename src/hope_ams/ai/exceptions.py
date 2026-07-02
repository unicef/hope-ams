class AIServiceError(Exception):
    """Base exception for AI service errors."""


class OllamaConnectionError(AIServiceError):
    """Could not connect to Ollama server."""


class OllamaTimeoutError(AIServiceError):
    """Request to Ollama timed out."""


class OllamaResponseError(AIServiceError):
    """Ollama returned an unexpected or unparseable response."""
