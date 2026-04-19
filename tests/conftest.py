from __future__ import annotations

from types import SimpleNamespace

import pytest


def make_response(text: str = "hi", prompt_tokens: int = 10,
                  completion_tokens: int = 5, total_tokens: int = 15,
                  reasoning_content: str | None = None):
    """Build a LiteLLM-shaped response object for mocking."""
    message = SimpleNamespace(content=text, reasoning_content=reasoning_content)
    choice = SimpleNamespace(message=message)
    usage = SimpleNamespace(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )
    return SimpleNamespace(choices=[choice], usage=usage)


@pytest.fixture
def fake_response():
    return make_response


@pytest.fixture
def mock_completion(mocker):
    """Patch litellm.completion; returns the MagicMock for assertions."""
    mock = mocker.patch("litellm.completion", return_value=make_response())
    return mock
