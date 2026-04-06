# Atlas REPL — Node bridge logging boundary

`scripts/atlas_repl.py` runs Glimpse through a **Node one-liner** subprocess. That path uses **`console.log(JSON.stringify(...))`** to emit **one JSON object per successful run** on **stdout**.

## Contract

| Layer | Mechanism | Consumers |
|-------|-----------|-----------|
| Python | `subprocess.run(["node", "-e", script], capture_output=True)` | Parses **first line** of stdout as JSON |
| Node (Glimpse) | `console.log` | **Not** application logging — **structured bridge output** only |

## Rules

1. **Do not** route Node `console.log` through Python `structlog` without an explicit adapter (different processes).
2. **Do** keep each line as **valid JSON** when the pipeline succeeds or returns a controlled error object (`{ "error": "..." }`).
3. **Python** side should use normal logging (`logging` / `structlog` in future refactors) for diagnostics **about** the subprocess (timeouts, missing `node`, non-JSON stdout).
4. On failure, `try_glimpse_pipeline` returns `None` and the REPL continues with Echoes-only context — preserve that degradation path when changing the bridge.

## References

- Implementation: [scripts/atlas_repl.py](../scripts/atlas_repl.py) (`try_glimpse_pipeline`)
- Echoes standard: [CLAUDE.md](../CLAUDE.md) — structured logging for FastAPI/agent code paths; run the REPL with `uv run python scripts/atlas_repl.py` from the repo root.
