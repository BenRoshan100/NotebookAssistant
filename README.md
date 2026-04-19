# notebook-assistant

[![PyPI version](https://img.shields.io/pypi/v/notebook-assistant.svg)](https://pypi.org/project/notebook-assistant/)
[![Python versions](https://img.shields.io/pypi/pyversions/notebook-assistant.svg)](https://pypi.org/project/notebook-assistant/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/benroshan100/NotebookAssistant/actions/workflows/test.yml/badge.svg)](https://github.com/benroshan100/NotebookAssistant/actions/workflows/test.yml)

Bring-your-own-LLM chat assistant for Jupyter notebooks. Load a DataFrame or
markdown file, ask questions in plain English, get markdown-rendered answers
right in your cell — with the provider you already pay for.

Supports **OpenAI**, **Anthropic**, **Google Gemini**, **AWS Bedrock**, and
any OpenAI-compatible endpoint (e.g. **Euron**), routed through
[LiteLLM](https://github.com/BerriAI/litellm).

## Install

```bash
pip install notebook-assistant
```

For AWS Bedrock also install the `bedrock` extra (adds `boto3`):

```bash
pip install "notebook-assistant[bedrock]"
```

## Quickstart

Pick a provider, pass your key, ask a question.

### OpenAI

```python
from notebook_assistant import NotebookAssistant

assistant = NotebookAssistant(
    model="openai/gpt-4o",
    api_key="sk-...",   # or set OPENAI_API_KEY env var
)
assistant.ask("Give me three exploratory questions for a sales dataset.")
```

### Anthropic

```python
assistant = NotebookAssistant(
    model="anthropic/claude-3-5-sonnet-20241022",
    api_key="sk-ant-...",   # or ANTHROPIC_API_KEY
)
```

### Google Gemini

```python
assistant = NotebookAssistant(
    model="gemini/gemini-1.5-pro",
    api_key="...",   # or GEMINI_API_KEY
)
```

### AWS Bedrock

```python
assistant = NotebookAssistant(
    model="bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0",
    aws_region="ap-south-1",
    # aws_access_key_id / aws_secret_access_key optional — falls back to
    # boto3's standard credential chain (env vars, IAM role, ~/.aws/credentials).
)
```

You can also pass an inference-profile ARN as the model id.

### Euron (OpenAI-compatible)

```python
assistant = NotebookAssistant(
    model="openai/gpt-5.3-instant",
    api_key="...",   # your Euron API key
    api_base="https://api.euron.one/api/v1/euri",
)
```

Any other OpenAI-compatible endpoint works the same way — pass
`model="openai/<name>"` with a matching `api_base`.

## Loading context

```python
import pandas as pd
from notebook_assistant import NotebookAssistant

df = pd.read_csv("sales.csv")

assistant = NotebookAssistant(model="openai/gpt-4o", api_key="sk-...")
assistant.add_context(
    instructions="Focus on month-over-month trends.",
    dataframes={"sales": df},
    markdown_path="docs/glossary.md",   # optional
)

assistant.ask("Which product saw the steepest decline last quarter?")
```

`add_context` accepts any combination of `instructions`, `dataframes`, and
`markdown_path`. The content becomes the first user message in the
conversation so every follow-up question sees it.

## Interactive chat

```python
assistant.chat()   # type 'exit' to quit
```

## Conversation management

```python
assistant.history   # list of {"role", "content"} dicts
assistant.reset()   # clear context and history
```

## Configuration reference

| Argument | Description |
|---|---|
| `model` | LiteLLM-style string: `<provider>/<model>`. See the [LiteLLM provider list](https://docs.litellm.ai/docs/providers). |
| `api_key` | Provider API key. If omitted, LiteLLM reads the provider's standard env var. |
| `api_base` | Override endpoint — for Euron or self-hosted OpenAI-compatible gateways. |
| `aws_region`, `aws_access_key_id`, `aws_secret_access_key`, `aws_session_token` | Bedrock-specific credentials. Fall back to the boto3 credential chain. |
| `system_prompt` | Custom system prompt. Defaults to a data-analysis-focused prompt. |
| `temperature` | Sampling temperature (default `0.2`). |
| `max_tokens` | Max response tokens (default `2048`). |
| `read_timeout` | Per-request timeout in seconds (default `60`). |

## Examples

- [`examples/quickstart.ipynb`](examples/quickstart.ipynb) — end-to-end walkthrough
  with multiple providers.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues and PRs welcome.

## License

[MIT](LICENSE)
