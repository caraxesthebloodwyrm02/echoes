# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**EchoesAssistantV2** is a multimodal AI assistant platform with 8 interconnected core intelligence modules, parallel simulation, WebSocket streaming, and consent-based licensing.

**Python**: 3.12+
**Stack**: FastAPI, LangChain, OpenAI, Pydantic v2, structlog
**Package Manager**: pip or uv (`pip install -e ".[dev]"` or `uv sync`)

## Commands

```bash
# Session start protocol — run before writing any new code
python -m pytest tests/ -q --tb=short && ruff check .

# Testing
python -m pytest tests/ -q --tb=short        # Full pytest suite
python test_integration_quick.py              # Quick validation (~2 seconds, no API calls)
python test_integration.py                    # Full integration (requires OpenAI key)

# Code quality
ruff check .                                  # Lint
black .                                       # Format
mypy .                                        # Type check

# Run
python assistant_v2_core.py                   # Interactive CLI assistant
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000  # API server
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
