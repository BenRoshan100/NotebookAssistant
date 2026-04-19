from __future__ import annotations

import pandas as pd
import pytest

from notebook_assistant import Answer, NotebookAssistant
from tests.conftest import make_response


def _make_assistant(**overrides) -> NotebookAssistant:
    defaults = dict(model="openai/gpt-4o", api_key="sk-test")
    defaults.update(overrides)
    return NotebookAssistant(**defaults)


def test_ask_returns_answer_with_usage(mock_completion):
    mock_completion.return_value = make_response(
        text="Here is the analysis.",
        prompt_tokens=42, completion_tokens=7, total_tokens=49,
    )
    assistant = _make_assistant()

    answer = assistant.ask("What is X?")

    assert isinstance(answer, Answer)
    assert answer.text == "Here is the analysis."
    assert answer.usage == {
        "input_tokens": 42,
        "output_tokens": 7,
        "total_tokens": 49,
    }


def test_ask_appends_user_and_assistant_turns(mock_completion):
    mock_completion.return_value = make_response(text="ok")
    assistant = _make_assistant()

    assistant.ask("first")
    assistant.ask("second")

    history = assistant.history
    assert [m["role"] for m in history] == ["user", "assistant", "user", "assistant"]
    assert history[0]["content"] == "first"
    assert history[2]["content"] == "second"


def test_ask_uses_default_system_prompt(mock_completion):
    assistant = _make_assistant()
    assistant.ask("hi")

    sent_messages = mock_completion.call_args.kwargs["messages"]
    assert sent_messages[0]["role"] == "system"
    assert "data analysis assistant" in sent_messages[0]["content"].lower()


def test_ask_respects_custom_system_prompt(mock_completion):
    assistant = _make_assistant(system_prompt="You are a pirate.")
    assistant.ask("hi")

    sent_messages = mock_completion.call_args.kwargs["messages"]
    assert sent_messages[0] == {"role": "system", "content": "You are a pirate."}


def test_ask_max_tokens_override(mock_completion):
    assistant = _make_assistant(max_tokens=100)
    assistant.ask("hi", max_tokens=999)

    assert mock_completion.call_args.kwargs["max_tokens"] == 999


def test_ask_empty_response_fallback(mock_completion):
    mock_completion.return_value = make_response(text="")
    assistant = _make_assistant()

    answer = assistant.ask("hi")

    assert answer.text == "_No response generated._"


def test_reset_clears_history(mock_completion):
    assistant = _make_assistant()
    assistant.ask("hi")
    assert len(assistant.history) == 2

    assistant.reset()

    assert assistant.history == []
    assert assistant._context_loaded is False


def test_add_context_with_instructions(mock_completion):
    assistant = _make_assistant()
    assistant.add_context(instructions="Focus on trends.")

    assert len(assistant.history) == 1
    assert assistant.history[0]["role"] == "user"
    assert "Focus on trends." in assistant.history[0]["content"]
    assert "ANALYSIS INSTRUCTIONS" in assistant.history[0]["content"]


def test_add_context_with_dataframe(mock_completion):
    df = pd.DataFrame({"sales": [100, 200], "region": ["N", "S"]})
    assistant = _make_assistant()
    assistant.add_context(dataframes={"sales_df": df})

    content = assistant.history[0]["content"]
    assert "DataFrame: sales_df" in content
    assert "2 rows x 2 columns" in content


def test_add_context_requires_something():
    assistant = _make_assistant()
    with pytest.raises(ValueError, match="at least one"):
        assistant.add_context()


def test_add_context_warns_on_overwrite(mock_completion):
    assistant = _make_assistant()
    assistant.add_context(instructions="first")

    with pytest.warns(UserWarning, match="Overwriting"):
        assistant.add_context(instructions="second")


def test_add_context_with_markdown_file(tmp_path):
    md = tmp_path / "ref.md"
    md.write_text("# Glossary\nMoM = month over month", encoding="utf-8")

    assistant = _make_assistant()
    assistant.add_context(markdown_path=md)

    content = assistant.history[0]["content"]
    assert "REFERENCE DOCUMENTATION" in content
    assert "MoM = month over month" in content


def test_add_context_returns_self_for_chaining(mock_completion):
    assistant = _make_assistant()
    result = assistant.add_context(instructions="hi")
    assert result is assistant


def test_answer_markdown_rendering():
    answer = Answer(
        "The analysis shows X.",
        usage={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
    )
    md = answer._repr_markdown_()

    assert "The analysis shows X." in md
    assert "input: 10" in md
    assert "output: 5" in md
    assert "total: 15" in md


def test_answer_without_usage():
    answer = Answer("hello")
    assert answer._repr_markdown_() == "hello"
    assert str(answer) == "hello"


def test_chat_falls_back_to_stdin_when_ipywidgets_missing(mock_completion, mocker):
    assistant = _make_assistant()
    # Force the widget path to fail the import.
    mocker.patch.object(assistant, "_chat_widgets", side_effect=ImportError("no widgets"))
    stdin_fallback = mocker.patch.object(assistant, "_chat_stdin")

    assistant.chat()

    stdin_fallback.assert_called_once()


def test_chat_prefers_widgets_when_available(mocker):
    assistant = _make_assistant()
    widget_path = mocker.patch.object(assistant, "_chat_widgets")
    stdin_fallback = mocker.patch.object(assistant, "_chat_stdin")

    assistant.chat()

    widget_path.assert_called_once()
    stdin_fallback.assert_not_called()


def test_constructor_forwards_bedrock_credentials(mock_completion):
    assistant = NotebookAssistant(
        model="bedrock/claude",
        aws_region="us-east-1",
        aws_access_key_id="AKIA",
        aws_secret_access_key="secret",
    )
    assistant.ask("hi")

    kwargs = mock_completion.call_args.kwargs
    assert kwargs["aws_region_name"] == "us-east-1"
    assert kwargs["aws_access_key_id"] == "AKIA"
    assert kwargs["aws_secret_access_key"] == "secret"
