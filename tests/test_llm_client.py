from __future__ import annotations

import pytest

from notebook_assistant.llm_client import LLMClient, LLMClientError


def test_complete_prepends_system_message(mock_completion):
    client = LLMClient(model="openai/gpt-4o", api_key="sk-test")
    client.complete(
        messages=[{"role": "user", "content": "hi"}],
        system="You are helpful.",
        temperature=0.3,
        max_tokens=100,
    )

    kwargs = mock_completion.call_args.kwargs
    assert kwargs["messages"][0] == {"role": "system", "content": "You are helpful."}
    assert kwargs["messages"][1] == {"role": "user", "content": "hi"}
    assert kwargs["model"] == "openai/gpt-4o"
    assert kwargs["api_key"] == "sk-test"
    assert kwargs["temperature"] == 0.3
    assert kwargs["max_tokens"] == 100


def test_complete_omits_none_credentials(mock_completion):
    client = LLMClient(model="openai/gpt-4o")
    client.complete(messages=[{"role": "user", "content": "hi"}])

    kwargs = mock_completion.call_args.kwargs
    assert "api_key" not in kwargs
    assert "api_base" not in kwargs
    assert "aws_region_name" not in kwargs


def test_complete_passes_bedrock_credentials(mock_completion):
    client = LLMClient(
        model="bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0",
        aws_region="ap-south-1",
        aws_access_key_id="AKIA...",
        aws_secret_access_key="secret",
        aws_session_token="token",
    )
    client.complete(messages=[{"role": "user", "content": "hi"}])

    kwargs = mock_completion.call_args.kwargs
    assert kwargs["aws_region_name"] == "ap-south-1"
    assert kwargs["aws_access_key_id"] == "AKIA..."
    assert kwargs["aws_secret_access_key"] == "secret"
    assert kwargs["aws_session_token"] == "token"


def test_complete_passes_api_base_for_euron(mock_completion):
    client = LLMClient(
        model="openai/gpt-5.3-instant",
        api_key="euron-key",
        api_base="https://api.euron.one/api/v1/euri",
    )
    client.complete(messages=[{"role": "user", "content": "hi"}])

    kwargs = mock_completion.call_args.kwargs
    assert kwargs["api_base"] == "https://api.euron.one/api/v1/euri"
    assert kwargs["api_key"] == "euron-key"


def test_complete_without_system(mock_completion):
    client = LLMClient(model="openai/gpt-4o")
    client.complete(messages=[{"role": "user", "content": "hi"}], system=None)

    msgs = mock_completion.call_args.kwargs["messages"]
    assert msgs == [{"role": "user", "content": "hi"}]


def test_complete_wraps_provider_errors(mocker):
    mocker.patch("litellm.completion", side_effect=RuntimeError("rate limited"))
    client = LLMClient(model="openai/gpt-4o")

    with pytest.raises(LLMClientError, match="LLM completion failed"):
        client.complete(messages=[{"role": "user", "content": "hi"}])


def test_timeout_forwarded(mock_completion):
    client = LLMClient(model="openai/gpt-4o", timeout=123)
    client.complete(messages=[{"role": "user", "content": "hi"}])

    assert mock_completion.call_args.kwargs["timeout"] == 123


def test_drop_params_enabled(mock_completion):
    """Unsupported params (e.g. temperature on GPT-5) should be silently
    dropped instead of raising — critical for a bring-your-own-model library
    where LiteLLM can't know every provider's quirks."""
    client = LLMClient(model="openai/gpt-4o")
    client.complete(messages=[{"role": "user", "content": "hi"}])

    assert mock_completion.call_args.kwargs["drop_params"] is True
