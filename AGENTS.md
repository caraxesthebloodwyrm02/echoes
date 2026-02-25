# AGENTS.md

## Cursor Cloud specific instructions

### Project Overview
EchoesAssistantV2 is a Python 3.12+ multimodal AI assistant platform with 8 interconnected core modules, a FastAPI WebSocket API, and a CLI assistant. See `README.md` for full details.

### Services

| Service | Command | Notes |
|---------|---------|-------|
| Core modules / CLI | `source venv/bin/activate && python test_integration_quick.py` | No API key needed; validates all 8 core modules |
| FastAPI API | `source venv/bin/activate && python -m uvicorn api.main:app --host 0.0.0.0 --port 8000` | Requires `OPENAI_API_KEY` env var. **Known issue:** `api/config.py` imports `BaseSettings` from `pydantic` instead of `pydantic_settings`; this must be fixed before the API server can start with pydantic v2. |

### Running Tests

- **Quick integration test (no API key):** `python test_integration_quick.py`
- **Pytest suite:** `python -m pytest tests/ --no-cov --timeout=30 --ignore=tests/glimpse -v`
  - Some test files fail to collect due to import errors (pre-existing): `tests/glimpse/`, `tests/test_all_demos.py`, `tests/test_display.py`, `tests/test_e2e_flow.py`, `tests/test_env.py`, `tests/test_exporter.py`, `tests/test_rag_orbit.py`, `tests/test_rag_setup.py`, `tests/test_rag_system.py`, `tests/test_rate_limiter.py`. Add `--ignore=` for each to avoid collection errors.
  - 76 tests pass; 10 failures and 5 skips are pre-existing.
  - The `--cov-fail-under=75` in `pytest.ini` will cause `pytest` to exit non-zero due to low coverage. Use `--no-cov` to skip coverage enforcement during development.

### Linting

- **Ruff:** `ruff check .` (configured in `pyproject.toml`)
- **Black:** `black --check .` (configured in `pyproject.toml`)
- Pre-existing lint issues exist across the codebase.

### Known Gotchas

1. **Dependency conflict:** `requirements.txt` specifies `langchain-core>=1.0.1,<2.0.0` but `langchain==0.3.21` requires `langchain-core<1.0.0`. Use `pip install -r requirements.txt --use-deprecated=legacy-resolver` to work around this.
2. **Pydantic v2 import:** `api/config.py` uses `from pydantic import BaseSettings` which was valid in pydantic v1 but fails with v2. The fix is `from pydantic_settings import BaseSettings`, but this is existing code.
3. **pytest.ini coverage:** Has `--cov-fail-under=75` which fails. Use `--no-cov` flag when running tests.
4. **Virtual environment:** The venv is at `/workspace/venv`. Always activate with `source venv/bin/activate` before running commands.
5. **`python3.12-venv`** system package is required but not pre-installed; the update script handles venv creation.
