from __future__ import annotations

import pandas as pd

from notebook_assistant.utils import dataframe_to_context, extract_text
from tests.conftest import make_response


def test_extract_text_returns_content():
    response = make_response(text="hello world")
    assert extract_text(response) == "hello world"


def test_extract_text_strips_whitespace():
    response = make_response(text="  padded  \n")
    assert extract_text(response) == "padded"


def test_extract_text_falls_back_to_reasoning_when_content_empty():
    response = make_response(text="", reasoning_content="thinking...")
    assert extract_text(response) == "thinking..."


def test_extract_text_returns_empty_when_nothing_available():
    response = make_response(text="")
    assert extract_text(response) == ""


def test_extract_text_handles_garbage_input():
    assert extract_text(None) == ""
    assert extract_text("not a response") == ""
    assert extract_text({}) == ""


def test_dataframe_to_context_small_df():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    ctx = dataframe_to_context(df, name="demo")

    assert "### DataFrame: demo" in ctx
    assert "3 rows x 2 columns" in ctx
    assert "Columns: a, b" in ctx
    assert "**Full data:**" in ctx
    assert "**Statistical summary:**" in ctx


def test_dataframe_to_context_large_df_is_truncated():
    df = pd.DataFrame({"x": range(500)})
    ctx = dataframe_to_context(df, name="big")

    assert "First 50 rows (of 500)" in ctx
    assert "**Full data:**" not in ctx
