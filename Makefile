install:
	uv sync

dev:
	uv run uvicorn api.main:app --reload

test:
	uv run pytest tests/ -v --tb=short

lint:
	ruff check api/ app/ glimpse/ tools/
	ruff format --check api/ app/

format:
	ruff format api/ app/ glimpse/ tools/
