from __future__ import annotations

from typing import Any


class LLMClientError(Exception):
    """Raised when an LLM completion call fails."""


class LLMClient:
    """Thin wrapper around `litellm.completion` supporting any provider LiteLLM supports.

    The `model` string selects the provider using LiteLLM's prefix convention:

    * ``openai/gpt-4o``
    * ``anthropic/claude-3-5-sonnet-20241022``
    * ``gemini/gemini-1.5-pro``
    * ``bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0``
    * ``openai/<euron-model>`` with ``api_base="https://api.euron.one/api/v1/euri"``
      for Euron (OpenAI-compatible).

    If ``api_key`` is None LiteLLM falls back to the provider's standard
    environment variable (``OPENAI_API_KEY``, ``ANTHROPIC_API_KEY``,
    ``GEMINI_API_KEY``, AWS credential chain, etc.).
    """

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        api_base: str | None = None,
        aws_region: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_session_token: str | None = None,
        timeout: int = 60,
    ):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.aws_region = aws_region
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token
        self.timeout = timeout

    def complete(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> Any:
        """Call the LLM and return the raw LiteLLM ``ModelResponse``."""
        full_messages: list[dict[str, str]] = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": self.timeout,
            "drop_params": True,
        }
        if self.api_key is not None:
            kwargs["api_key"] = self.api_key
        if self.api_base is not None:
            kwargs["api_base"] = self.api_base
        if self.aws_region is not None:
            kwargs["aws_region_name"] = self.aws_region
        if self.aws_access_key_id is not None:
            kwargs["aws_access_key_id"] = self.aws_access_key_id
        if self.aws_secret_access_key is not None:
            kwargs["aws_secret_access_key"] = self.aws_secret_access_key
        if self.aws_session_token is not None:
            kwargs["aws_session_token"] = self.aws_session_token

        try:
            import litellm
        except ImportError as exc:
            raise LLMClientError(
                "litellm is not installed. Install notebook-assistant with "
                "`pip install notebook-assistant`."
            ) from exc

        try:
            return litellm.completion(**kwargs)
        except Exception as exc:
            raise LLMClientError(f"LLM completion failed: {exc}") from exc
