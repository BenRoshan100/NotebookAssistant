from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from notebook_assistant.llm_client import LLMClient
from notebook_assistant.prompts import DEFAULT_SYSTEM_PROMPT
from notebook_assistant.utils import dataframe_to_context, extract_text

if TYPE_CHECKING:
    import pandas as pd


class Answer:
    """Wraps an LLM response so Jupyter renders it as markdown automatically.

    - Last expression in a cell -> rendered as markdown (no duplicate text)
    - print(answer) -> plain text
    - str(answer) -> raw string
    """

    def __init__(self, text: str, usage: dict | None = None):
        self.text = text
        self.usage = usage or {}

    def _repr_markdown_(self) -> str:
        parts = [self.text]
        if self.usage:
            parts.append(self._usage_footer())
        return "\n\n".join(parts)

    def _usage_footer(self) -> str:
        input_tokens = self.usage.get("input_tokens", "N/A")
        output_tokens = self.usage.get("output_tokens", "N/A")
        total = self.usage.get("total_tokens", "N/A")
        return (
            f"---\n"
            f"*Tokens -- input: {input_tokens} | output: {output_tokens} | total: {total}*"
        )

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return self.text


class NotebookAssistant:
    """Interactive data analysis assistant backed by any LiteLLM-supported provider.

    Parameters
    ----------
    model : str
        LiteLLM-style model string, e.g. ``openai/gpt-4o``,
        ``anthropic/claude-3-5-sonnet-20241022``, ``gemini/gemini-1.5-pro``,
        ``bedrock/<inference-profile-arn>`` or ``openai/<model>`` paired with
        a custom ``api_base`` for OpenAI-compatible providers such as Euron.
    api_key : str | None
        Provider API key. If omitted, LiteLLM reads the provider's standard
        environment variable (``OPENAI_API_KEY``, ``ANTHROPIC_API_KEY``,
        ``GEMINI_API_KEY``, etc.).
    api_base : str | None
        Override the provider endpoint. Use this for Euron
        (``https://api.euron.one/api/v1/euri``) or any self-hosted
        OpenAI-compatible endpoint.
    aws_region, aws_access_key_id, aws_secret_access_key, aws_session_token : str | None
        Bedrock-specific credentials. Falls back to the boto3 credential
        chain when unset.
    system_prompt : str | None
        Custom system prompt. Falls back to ``DEFAULT_SYSTEM_PROMPT``.
    temperature : float
        Sampling temperature (default: 0.2).
    max_tokens : int
        Max response tokens (default: 2048).
    read_timeout : int
        Per-request timeout in seconds (default: 60).
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
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        read_timeout: int = 60,
    ):
        self._client = LLMClient(
            model=model,
            api_key=api_key,
            api_base=api_base,
            aws_region=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            timeout=read_timeout,
        )
        self._system = system_prompt or DEFAULT_SYSTEM_PROMPT
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._messages: list[dict[str, str]] = []
        self._context_loaded = False

    # ── Context loading ──────────────────────────────

    def add_context(
        self,
        *,
        instructions: str = "",
        dataframes: dict[str, "pd.DataFrame"] | None = None,
        markdown_path: str | Path | None = None,
    ) -> "NotebookAssistant":
        """Load reference material into the conversation as the first message."""
        parts: list[str] = []

        if markdown_path:
            md_text = Path(markdown_path).read_text(encoding="utf-8")
            parts.append(f"## REFERENCE DOCUMENTATION\n{md_text}")

        if dataframes:
            parts.append("## DATA CONTEXT")
            for name, df in dataframes.items():
                parts.append(dataframe_to_context(df, name))

        if instructions:
            parts.append(
                f"## ANALYSIS INSTRUCTIONS\n{instructions}\n\n"
                "NOTE:\n"
                "- All numeric values are already computed.\n"
                "- Do NOT recalculate or estimate values.\n"
                "- Perform interpretation, comparison, and insight generation only."
            )

        if not parts:
            raise ValueError(
                "Provide at least one of: instructions, dataframes, markdown_path"
            )

        if self._context_loaded:
            import warnings
            warnings.warn(
                "Overwriting existing context. Previous conversation will be lost.",
                stacklevel=2,
            )

        context_msg = "\n\n".join(parts)
        self._messages = [{"role": "user", "content": context_msg}]
        self._context_loaded = True
        return self

    # ── Single question ──────────────────────────────

    def ask(
        self,
        question: str,
        max_tokens: int | None = None,
    ) -> Answer:
        """Send a single question and return an ``Answer``."""
        self._messages.append({"role": "user", "content": question})

        response = self._client.complete(
            messages=self._messages,
            system=self._system,
            temperature=self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )

        text = extract_text(response) or "_No response generated._"
        self._messages.append({"role": "assistant", "content": text})

        return Answer(text, _usage_to_dict(response))

    # ── Interactive loop ─────────────────────────────

    def chat(self) -> None:
        """Start an interactive chat inside the notebook.

        Uses ``ipywidgets`` when available (reliable in Jupyter, VS Code,
        and SageMaker). Falls back to stdin ``input()`` if ipywidgets isn't
        installed or a display environment isn't available.
        """
        try:
            self._chat_widgets()
        except ImportError:
            self._chat_stdin()

    def _chat_widgets(self) -> None:
        import ipywidgets as widgets
        from IPython.display import Markdown, clear_output, display

        output = widgets.Output(layout=widgets.Layout(
            border="1px solid #ddd",
            padding="8px",
            max_height="500px",
            overflow_y="auto",
        ))
        text_input = widgets.Text(
            placeholder="Ask a question… (Enter to send)",
            layout=widgets.Layout(flex="1"),
        )
        send_button = widgets.Button(description="Send", button_style="primary")
        reset_button = widgets.Button(description="Reset")

        def handle_send(_=None):
            question = text_input.value.strip()
            if not question:
                return
            text_input.value = ""
            with output:
                display(Markdown(f"**You:** {question}"))
            answer = self.ask(question)
            with output:
                display(answer)

        def handle_reset(_):
            self.reset()
            with output:
                clear_output()
                display(Markdown("*Conversation reset.*"))

        send_button.on_click(handle_send)
        reset_button.on_click(handle_reset)
        text_input.on_submit(handle_send)

        hint = "Context loaded." if self._context_loaded else "No context loaded."
        with output:
            display(Markdown(f"*{hint} Type a question and press Enter, or click Send.*"))

        display(output)
        display(widgets.HBox([text_input, send_button, reset_button]))

    def _chat_stdin(self) -> None:
        if self._context_loaded:
            print("Context loaded. Ask questions below. Type 'exit' to quit.\n")
        else:
            print("No context loaded. You can still ask questions. Type 'exit' to quit.\n")

        while True:
            try:
                question = input("You: ")
            except (EOFError, KeyboardInterrupt):
                print("\nSession ended.")
                break

            if question.strip().lower() in {"exit", "quit", ""}:
                break

            answer = self.ask(question)
            self._display(answer)

    # ── Conversation management ──────────────────────

    def reset(self) -> None:
        """Clear conversation history and context."""
        self._messages.clear()
        self._context_loaded = False

    @property
    def history(self) -> list[dict[str, str]]:
        """Return a copy of the conversation message list."""
        return list(self._messages)

    # ── Display ──────────────────────────────────────

    @staticmethod
    def _display(answer: "Answer") -> None:
        try:
            from IPython.display import display
            display(answer)
        except ImportError:
            print(answer)


def _usage_to_dict(response: Any) -> dict:
    """Normalise LiteLLM ``response.usage`` into a plain dict."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return {}
    return {
        "input_tokens": getattr(usage, "prompt_tokens", None),
        "output_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }
