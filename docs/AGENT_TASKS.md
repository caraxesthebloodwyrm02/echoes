# AGENT_TASKS.md — Research-Lab Macro Pipeline v3.0

This file guides contributors and IDE agents through daily operations, guardrails, and deliverables for the unified physical + cognitive lab.

## 1) Pre-Flight (run locally before any PR)

- Format/lint:
  - `black . && isort . && autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r .`
  - Or: `python tools/format_all.py`
- Tests: `pytest -q`
- Pre-commit: `pre-commit run --all-files`
- Ensure no untracked large files or nested `.git/` directories.

## 2) Branching, Commits, PR Gate

- Branch names: `feat/...`, `fix/...`, `test/...`, `ci/...`, `docs/...`
- Commit tags: `feat:`, `fix:`, `test:`, `ci:`, `docs:`
- PR must show:
  - `pytest` output (all green)
  - JSON schema checks for new data (if applicable)
  - No formatting diffs after `tools/format_all.py`

## 3) Roles & Responsibilities (parallel specialization)

- Systems/CI
  - Maintain pre-commit, ensure CI jobs: format-lint, pytest, json-schema
  - Keep <5% CI failure rate; triage flaky tests immediately
- Simulation
  - Implement `demo/kalman.py`, `demo/headsweep.py`
  - Emit logs to `data/physics/` (CSV/JSON): `{t, state_est, meas, residual}`
- Linguistics
  - Implement `speech/pause_model.py` baseline (prosody, gaps, filler)
  - Use `data/podcasts/` JSONL: `{timestamp, pause_type, sentiment_shift, prosody}`
- Macro Architect
  - Orchestrate `workflows/macro.py` Phases A–D
  - Deterministic merge w/ priority map and merge log in `reports/`
- Data QA
  - Validate schemas, verify metrics, sign artifacts
  - Ensure tests for merge and schemas stay green

## 4) Macro Orchestration (Phase A–D)

- Phase A: baselines (Kalman, pause baseline)
- Phase B: enrichment (headsweep, prosody)
- Phase C: patch (prompt-engine corrections)
- Phase D: finalization (merge + polish)
- Deterministic merge rule (priority highest wins on conflicts): `D=3 > C=2 > B=1 > A=0`
- Record overwrites to `reports/merge_log_YYYYMMDD.json`

## 5) Run Recipes (incremental)

- Physical: run `demo/kalman.py` against sample input; compare to `demo/headsweep.py` output
- Cognitive: run `speech/pause_model.py` over `data/podcasts/` snippets
- Macro (skeleton): `python -c "from workflows.macro import run_macro; print(run_macro('ABCD'))"`

## 6) Data & Schemas

- Physics logs (`data/physics/`): CSV/JSON
  - schema: `t: float`, `state_est: list[float]`, `meas: list[float]`, `residual: list[float]`
- Pause annotations (`data/podcasts/`): JSONL
  - schema: `timestamp: float`, `pause_type: str`, `prosody: dict`, `sentiment_shift: float`
- Macro artifacts (`reports/`): MD/JSON
  - `reports/macro_run_YYYYMMDD.md` summary
  - `reports/merge_log_YYYYMMDD.json` for conflict audit

## 7) Packaging Checklist

- Include: `demo/`, `speech/`, `workflows/`, `tests/`, `docs/`, `data/samples/`, `AGENT_TASKS.md`, `LICENSE`, `requirements.txt`
- Command: `zip -r deliverable_snapshot.zip demo speech workflows tests docs data scripts AGENT_TASKS.md LICENSE requirements.txt`

## 8) Quality Gates & Metrics

- Simulation accuracy: Kalman residual RMSE reduction ≥ 25%
- Semantic precision: pause classification +10% vs. baseline
- Prompt reuse: cache hit-rate ≥ 20%
- Macro stability: merge conflicts ≤ 2%
- Dev efficiency: ≤ 2 min time-to-commit
- CI reliability: < 5% failure

## 9) Guardrails

- Bounded loops for demos
- Deterministic seeds for examples
- No secrets in code; use `.env` and CI secrets
- JSON schema validation on new data files

## 10) Definition of Done (per change)

- Code formatted, linted, and tested locally
- Updated docs/tests if behavior changed
- Artifacts produce correct schema; macro merge stable
- PR created with evidence (test logs, sample artifacts)
