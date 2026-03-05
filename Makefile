# Align with GRID-main: uv as package manager, .venv, dev+test groups
install:
	uv sync --group dev --group test

dev:
	uv run uvicorn api.main:app --reload

# Default test run: no coverage (fast, CI-aligned)
test:
	uv run pytest tests/ -v --tb=short

# Coverage run: report only (fail_under=0 in .coveragerc)
coverage:
	uv run pytest tests/ -v --tb=short --cov=app --cov=api --cov=glimpse --cov=tools --cov=core --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml

lint:
	ruff check api/ app/ glimpse/ tools/
	ruff format --check api/ app/ glimpse/ tools/

format:
	ruff format api/ app/ glimpse/ tools/
