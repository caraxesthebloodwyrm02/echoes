# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**EchoesAssistantV2** is a multimodal AI assistant platform with 8 interconnected core intelligence modules, parallel simulation, WebSocket streaming, and consent-based licensing.

**Python**: 3.13+ (see `requires-python` in `pyproject.toml`)
**Stack**: FastAPI, LangChain, OpenAI, Pydantic v2, structlog
**Package Manager**: **uv** (canonical). Install deps: `uv sync --group dev --group test` or `make install`. Prefer `uv run …` for pytest, ruff, mypy, and scripts so the project venv and lockfile are always used.

## Commands

```bash
# Session start protocol — run before writing any new code
uv run pytest tests/ -q --tb=short && uv run ruff check .

# Testing
make test                                     # uv run pytest tests/ -v --tb=short
uv run pytest tests/ -q --tb=short            # Full pytest suite
uv run python test_integration_quick.py       # Quick validation (~2 seconds, no API calls)
uv run python test_integration.py             # Full integration (requires OpenAI key)

# Atlas gates
uv run pytest tests/test_atlas_integration.py -q
uv run python scripts/atlas_drift_check.py

# Code quality
uv run ruff check .                           # Lint
uv run ruff format .                          # Format
uv run mypy .                                  # Type check

# Run
uv run python assistant_v2_core.py          # Interactive CLI assistant
make dev                                      # uv run uvicorn api.main:app --reload
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000  # API server
```

## Architecture

### 8 Core Modules (`core_modules/`)
1. **Parallel Simulation Engine** — concurrent scenario exploration (up to 16 threads)
2. **Intent Awareness Engine** — NLP with 28+ intent types
3. **Thought Tracking System** — cognitive relationship mapping
4. **Personality Engine** — adaptive emotional intelligence
5. **Humor Engine** — context-aware humor
6. **Cross-Reference System** — dynamic knowledge connection
7. **Catch & Release Caching** — intelligent memory management
8. **Value System** — ethical reasoning framework

### Key Layers
- **`api/`** — FastAPI server: WebSocket streaming (`/ws/stream`), REST endpoints, JWT + API key auth, Prometheus metrics (`/metrics`)
- **`app/agents/`** — AI agent orchestration
- **`app/resilience/`** — circuit breakers (pybreaker), rate limiting (SlowApi), retry (tenacity)
- **`app/knowledge/`** — context and memory management
- **`core_modules/`** — the 8 intelligence modules above
- **`assistant_v2_core.py`** — main interactive CLI entry point

## Code Standards

- Type hints required on all function signatures
- Async-first: prefer `async def` for I/O operations
- FastAPI with dependency injection (`Depends()`)
- Pydantic v2 for data models
- Structured logging with `structlog` — no bare `print()` in production
- snake_case for all Python files
- Conventional commits: `fix(api):`, `feat(assistant):`, `refactor(services):`, `test:`, `docs:`

## Safety Rules

- **Consent-Based License**: all data processing must respect consent boundaries
- **DCoC Provenance**: AI-generated content must carry provenance metadata (model, timestamp, confidence) — never strip provenance headers
- Never use `eval()`, `exec()`, or `pickle` on untrusted input
- Never interpolate user input into prompts without sanitization
- Never remove or weaken existing validation logic
- Quarantined modules require explicit approval before modification

## Git hygiene and source protection

- Respect **`.gitignore`** and **`core.excludesfile`** when set (`~/.config/git/ignore` — see `~/scripts/global-git-excludes-README.md`). Do not stage generated output (`dist/`, `build/`, `.next/`, coverage, `.venv/`, `node_modules/`, `*.tsbuildinfo`), caches, local `.env*`, or IDE-only dirs unless the operator explicitly requests it.
- Prefer **`git status`** and **`git diff`** before **`git add`**. Avoid repository-wide **`git add .`**. Do not **force-push** or rewrite **history** without explicit instruction.
- Change **generators and source**, not hand-edited **`dist/`** or lockfiles, unless the task is explicitly to update those files.
- **Secrets:** Never commit credentials. If found tracked or staged, stop and escalate: **`.gitignore`**, **`git rm --cached`**, and rotation / history scrub are **human-gated** when pushes occurred.
- **New repos:** `~/seed/templates/gitignore-node-strict.template` or `gitignore-python-uv.template`. **Audit:** `~/scripts/gitignore-audit.sh`.

