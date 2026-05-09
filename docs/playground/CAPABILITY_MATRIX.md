# Capability matrix (playground)

Structured comparison when models, agents, or API surfaces change. Append new rows; do not rewrite history.

## Column definitions

| Column | Description |
|--------|-------------|
| **Date** | ISO date (UTC) of the run |
| **Surface** | Entry point: `assistant_v2_core` CLI, `api/main` HTTP, `glimpse/*`, `scripts/*`, etc. |
| **Scenario** | Short label for what was exercised |
| **API path** | `chat.completions` and/or `responses` (or `other`) |
| **Model** | Model id or env-sourced name |
| **Agent** | Human or tool (e.g. Cursor agent) + optional profile |
| **Command / check** | Exact command or automated check |
| **Pass criteria** | What “pass” means (exit code, test name, latency bound) |
| **Outcome** | `pass` / `partial` / `fail` + one-line note |

## Log (append below)

| Date | Surface | Scenario | API path | Model | Agent | Command / check | Pass criteria | Outcome |
|------|---------|----------|----------|-------|-------|-----------------|---------------|---------|
| 2026-05-10 | tests (store) | Outcome log + empirical probabilities | n/a (unit; no live OpenAI) | n/a | Cursor agent | `uv run python -m pytest tests/test_outcome_prediction_store.py tests/test_parallel_simulation_outcomes.py -q` | Exit 0; 7 tests passed | pass — deterministic; no `OPENAI_API_KEY` required |

## Template row (copy as a new table row)

```
| YYYY-MM-DD | | | | | | | | |
```
