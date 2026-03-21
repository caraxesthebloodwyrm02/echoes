# Echoes Copilot Instructions

## Review Guardrails

- Python 3.12+, type hints required on all functions and methods.
- Package manager: `uv` only — never `pip`, `poetry`, or `conda`.
- Logging: `structlog` — no `print()` in runtime paths.
- Never commit secrets, keys, or `.env` files. Use `pydantic-settings` for config.
- Keep changes narrow and production-oriented.
- Preserve FastAPI behavior and public interfaces unless the PR explicitly changes them.

## Stack

FastAPI 0.120, Uvicorn, httpx (async), LangChain, scikit-learn, NumPy, Pandas.
Auth via PyJWT. Rate limiting: SlowAPI (inbound), tenacity (outbound retries), pybreaker (circuit breaker).
Testing: pytest. Linting: ruff (120-char line length). Type checking: mypy (strict).

## Commands

```bash
uv sync                        # Install deps
uv run ruff check .            # Lint
uv run ruff format --check .   # Format check
uv run mypy .                  # Type check
uv run pytest -q --tb=short    # Tests
```

## Architecture (Layered)

- `app/api/v1/routers/` — Feature-based routers. Zod-like Pydantic DTOs at boundaries.
- `app/services/` — Business logic + outbound calls. Every external call must use retry + circuit breaker.
- `app/crud/` — DB operations only. No business logic here.
- `app/resilience/` — Rate limiting, retry, circuit breaker utilities.

## Code Review Focus

- **Resilience**: Outbound calls wrapped in tenacity retry + pybreaker circuit breaker.
- **Rate limiting**: Inbound endpoints use SlowAPI. Key must include user identity, not just IP.
- **Async**: All I/O must be async. Use `httpx.AsyncClient`, not `requests`.
- **Audit trail**: Echoes emits to `~/.echoes/audit.ndjson`. Changes to emission must preserve the contract.
- **Layer boundaries**: Routers → Services → CRUD. No skipping layers.
