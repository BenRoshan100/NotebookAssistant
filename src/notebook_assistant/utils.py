from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def extract_text(response: Any) -> str:
    """Pull assistant text from a LiteLLM ``ModelResponse``.

    LiteLLM normalises every provider to the OpenAI shape, so the answer is at
    ``response.choices[0].message.content``. Some reasoning models additionally
    expose ``reasoning_content`` on the message — we fall back to it only when
    ``content`` is empty.
    """
    try:
        message = response.choices[0].message
    except (AttributeError, IndexError, TypeError):
        return ""

    content = getattr(message, "content", None) or ""
    if isinstance(content, str) and content.strip():
        return content.strip()

    reasoning = getattr(message, "reasoning_content", None) or ""
    if isinstance(reasoning, str) and reasoning.strip():
        return reasoning.strip()

    return ""


def dataframe_to_context(df: "pd.DataFrame", name: str = "data") -> str:
    """Convert a DataFrame into an LLM-friendly context string.

    Includes shape, columns, .describe() summary, and row data
    (capped at 200 rows to avoid blowing context limits).
    """
    parts = [f"### DataFrame: {name}"]
    parts.append(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    parts.append(f"Columns: {', '.join(df.columns.tolist())}")

    parts.append("\n**Statistical summary:**")
    parts.append(df.describe(include="all").to_markdown())

    if len(df) <= 200:
        parts.append("\n**Full data:**")
        parts.append(df.to_markdown(index=False))
    else:
        parts.append(f"\n**First 50 rows (of {len(df)}):**")
        parts.append(df.head(50).to_markdown(index=False))

    return "\n".join(parts)
