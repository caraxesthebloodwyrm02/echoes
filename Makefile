.PHONY: install dev test coverage lint format docker-build docker-build-prod docker-up docker-down docker-logs

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
	uv run ruff check api/ app/ glimpse/ tools/
	uv run ruff format --check api/ app/ glimpse/ tools/

format:
	uv run ruff format api/ app/ glimpse/ tools/

docker-build: ## Build Echoes Docker image (dev)
	docker build -t echoes:dev --target dev .

docker-build-prod: ## Build Echoes Docker image (prod)
	docker build -t echoes:prod --target prod .

docker-up: ## Start Echoes with Redis
	docker compose up -d

docker-down: ## Stop Echoes containers
	docker compose down

docker-logs: ## Tail Echoes logs
	docker compose logs -f --tail=50
