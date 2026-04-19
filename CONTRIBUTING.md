# Contributing

Thanks for considering a contribution! This project is small and the bar is:
tests pass, the diff is focused, and the change is documented.

## Dev setup

```bash
git clone https://github.com/benroshan100/NotebookAssistant.git
cd NotebookAssistant
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev,bedrock]"
```

## Running checks

```bash
ruff check .
pytest
```

Tests mock `litellm.completion` — no network calls, no API keys required.

## Adding a provider

Every provider LiteLLM supports already works — users just pick the right
`model` prefix. If a provider needs special handling (extra kwargs,
non-standard error shapes), extend `LLMClient` in
[src/notebook_assistant/llm_client.py](src/notebook_assistant/llm_client.py)
and add a unit test.

## Release flow

1. Bump `version` in `pyproject.toml` and `src/notebook_assistant/__init__.py`.
2. Add a `## [x.y.z]` section to `CHANGELOG.md`.
3. Open a PR; merge once CI is green.
4. Tag the merge commit: `git tag v0.2.0 && git push --tags`.
5. `publish.yml` builds and uploads to PyPI via Trusted Publisher (OIDC).

The first release also requires a one-time
[PyPI Trusted Publisher](https://docs.pypi.org/trusted-publishers/) setup
on pypi.org pointing at this repo + the `publish.yml` workflow.

## Code style

- Ruff handles lint + import sorting.
- Keep the public API minimal — `NotebookAssistant`, `Answer`, `LLMClient`.
- No comments that restate what the code does. Only explain *why* when
  non-obvious.

## Reporting issues

Include: Python version, `notebook-assistant` version, provider + model,
and a minimal reproducer. Scrub any API keys.
