# Standards (Python + FastAPI)

Applies to: `api/**`, `src/**`, `core/**`, `services/**`, `models/**`

## Stack

- Python 3.12+ — use modern syntax (type unions with `|`, etc.)
- FastAPI with dependency injection (`Depends()`)
- setuptools + uv for dependency management
- LangChain for AI/LLM orchestration
- Structured logging with `structlog` or `logging` — no bare `print()` in production code
- Pydantic v2 for data models

## Dev Commands

- Run API: `python -m uvicorn api.main:app --host 0.0.0.0 --port 8000`
- Test: `python -m pytest tests/ -q --tb=short`
- Lint: `ruff check .`
- Install: `pip install -e ".[dev]"` or `uv sync`

## Conventions

- Type hints required on all function signatures
- Async-first: prefer `async def` for I/O operations
- File naming: snake_case for all Python files
- Named exports preferred; avoid wildcard imports

## Testing

- Use pytest with descriptive test names
- Integration tests for API endpoints with httpx/TestClient
- Unit tests for business logic in isolation
