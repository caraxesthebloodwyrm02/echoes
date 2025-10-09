# Tools Usage Guide

## Testing
- Run all unit tests: `make test` or `./tools.ps1 -Task test`
- Dash callback tests live in `tests/unit/test_dashboard_callbacks.py`

## Performance
- Run benchmarks and export baseline: `make perf` or `./tools.ps1 -Task perf`
- Output: `baseline_metrics.csv`

## Security
- Run safety, pip-audit, bandit: `make security` or `./tools.ps1 -Task security`

## Observability
- Start FastAPI app and verify:
  - `curl http://127.0.0.1:8000/api/metrics`
  - `curl http://127.0.0.1:8000/api/health`

## Load Testing
- Local quick run (3m): `make load`
- Customize via Locust CLI options

## Types & Lint
- Run strict type checks and linters: `make types`

## CI Workflows
- Security scans: `.github/workflows/security-scan.yml`
- Types & lint: `.github/workflows/types-lint.yml`
- Unit tests: `.github/workflows/tests.yml`
