#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  python3 -m pip install uv
fi

uv sync --frozen --group dev --group test
uv run --frozen ruff check .
uv run --frozen ruff format --check .
python3 -m compileall api app automation echoes glimpse src tools tests assistant_v2_core.py check_api_key.py legal_safeguards.py verify_environment.py
uv run --frozen pytest tests/ -q --tb=short --maxfail=5
uvx --from build pyproject-build
