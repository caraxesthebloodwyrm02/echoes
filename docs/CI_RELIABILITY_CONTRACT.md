# CI/CD Reliability Contract

This document defines the reliability contract for the Echoes CI/CD pipeline.

## Pipeline

| Field | Value |
|-------|-------|
| Name | echoes-ci |
| Repository | caraxesthebloodwyrm02/echoes |
| Default branch | main |

## Triggers

- **Push** and **Pull request** to `main`

## Jobs

### Lint

- **Timeout**: 5 minutes
- **Steps**: `ruff check api/ app/` and `ruff format --check api/ app/`
- **Success**: All steps exit 0
- **Scope**: Only `api/` and `app/` are linted; `glimpse/`, `tools/`, `core/`, `src/` are excluded

### Test

- **Timeout**: 10 minutes
- **Env**: `API_KEY_REQUIRED=false`
- **Command**: `pytest tests/ -v --tb=short --maxfail=10 --ignore=tests/test_quantum_state_integration.py --ignore=tests/benchmark_rate_limiter.py`
- **Success**: Exit code 0
- **Coverage**: Not enforced in CI (addopts override)

**Known skips:**

| Test | Reason |
|------|--------|
| test_rag_orbit | NumPy DLL load failure (Windows/Python 3.13) |
| test_quantum_state_integration | NumPy import chain; excluded from CI |
| test_coverage_completions | matplotlib not available |
| test_dashboard_callbacks | Q4 dashboard module not found |

**API-key dependent (fail without OPENAI_API_KEY):**

- test_all_demos
- test_agentic_assistant
- test_echoes_assistant_v2_comprehensive
- test_model_router (end-to-end flow)
- test_multi_agent_workflows

**Module-dependent:**

- test_ethos (requires `core.ethos`)

### Security

- **Timeout**: 5 minutes
- **Command**: `pip-audit --ignore-vuln CVE-2025-6984 --ignore-vuln CVE-2026-26013`
- **Success**: Exit code 0

### Gate

- **Needs**: lint, test, security
- **Success**: All upstream jobs succeeded

## Guarantees

1. Lint passes if and only if `api/` and `app/` pass ruff check and format.
2. Test passes if and only if pytest exits 0 with CI addopts (no coverage).
3. A push is green when lint, test, security, and gate all succeed.
4. Skipped/error tests: quantum (numpy), rag_orbit (numpy), demos/assistant (OPENAI_API_KEY), ethos (core.ethos), guardrails (c_o_r_e).

## Local verification

```bash
ruff check api/ app/ && ruff format --check api/ app/
pytest tests/ -v --tb=short --maxfail=10 --ignore=tests/test_quantum_state_integration.py --ignore=tests/benchmark_rate_limiter.py -o addopts="-ra --strict-markers --tb=short --maxfail=10"
pip-audit --ignore-vuln CVE-2025-6984 --ignore-vuln CVE-2026-26013
```

## Machine-readable contract

- `.github/ci_reliability_contract.yaml` — YAML contract
- `.github/schemas/ci_reliability_contract.json` — JSON Schema for validation
