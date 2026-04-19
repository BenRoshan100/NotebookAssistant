# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-04-18

### Added
- Multi-provider LLM support via [LiteLLM](https://github.com/BerriAI/litellm):
  OpenAI, Anthropic, Google Gemini, AWS Bedrock, and any OpenAI-compatible
  endpoint (e.g. Euron).
- `LLMClient` class (`notebook_assistant.llm_client`) — provider-agnostic
  wrapper around `litellm.completion`.
- Per-provider optional install extras: `pip install notebook-assistant[bedrock]`.
- MIT license, README, CHANGELOG, contributing guide, and test suite.
- GitHub Actions workflows for CI (lint + pytest matrix) and PyPI publishing
  via Trusted Publisher (OIDC).

### Changed
- **Breaking:** `NotebookAssistant` constructor signature. The first argument
  is now `model` (LiteLLM-style, e.g. `openai/gpt-4o`, `bedrock/<arn>`)
  instead of `model_id`. New optional parameters: `api_key`, `api_base`,
  `aws_region`, `aws_access_key_id`, `aws_secret_access_key`,
  `aws_session_token`.
- Default `max_tokens` reduced from 8000 to 2048, default `read_timeout` from
  600 to 60 (more sensible cross-provider defaults).
- `Answer.usage` dict keys changed from `inputTokens`/`outputTokens`/
  `totalTokens` to `input_tokens`/`output_tokens`/`total_tokens`.
- Internal message format switched from Bedrock blocks to OpenAI-style
  `{"role", "content"}` dicts. User-visible API (`ask`, `add_context`,
  `chat`, `reset`, `history`) is unchanged.

### Removed
- `notebook_assistant.bedrock` module (replaced by `llm_client`).
- `make_system_block` helper from `notebook_assistant.prompts`
  (no longer needed — system prompt passed directly).

### Migration

```python
# 0.1.0
NotebookAssistant(model_id="arn:...", region="ap-south-1")

# 0.2.0
NotebookAssistant(model="bedrock/arn:...", aws_region="ap-south-1")
```

## [0.1.0] - 2026-04-10

Initial Bedrock-only release.
