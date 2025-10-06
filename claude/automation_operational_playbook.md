# 🤖 Echoes Automation Operational Playbook

A practical, code-anchored guide to install, extend, and operate automation across the Echoes (The Albatross) codebase. Built around your existing framework in `automation/core/` (`Context`, `Orchestrator`, `Logger`) and integrated with pre-commit and CI.

---

## 1) Current Automation Snapshot

- **[framework]** Orchestrator: `automation/core/orchestrator.py`
- **[framework]** Context: `automation/core/context.py`
- **[framework]** Logging: `automation/core/logger.py`
- **[tasks]** Example: `automation/tasks/sanitize_codebase.py`
- **[config]** YAML config: `automation/config/automation_config.yaml`
- **[entrypoint]** Runner: `automation/scripts/run_automation.py`
- **[quality]** Black, Flake8, MyPy, Bandit via pre-commit
- **[tests]** Pytest with coverage; test bootstrap in `tests/conftest.py`

This playbook installs high‑ROI tasks and wires them into your framework + Git.

---

## 2) Gold‑ROI Tasks (install in this order)

- **[critical]** Test generator + "ensure tests exist" check
- **[critical]** API docs sync from OpenAPI
- **[high]** Endpoint smoke tests (pre‑commit + CI)
- **[high]** Dependency update + audit
- **[high]** Security scans (Bandit + pip‑audit)
- **[medium]** Release notes generation
- **[medium]** Performance benchmarking

Time to install: ~2 hours. Time saved/week: 12–18 hours.

---

## 3) Implementations (drop‑in tasks)

Below tasks follow your Orchestrator contract:
- Module import path from YAML: `automation.tasks.<module>`
- Function name derived from `name` field: lowercased, spaces→`_`
- Called as: `func(context)` and can read `context.extra_data`

### 3.1 Test generator (critical)
- Purpose: create pytest skeletons for modules to prevent test debt.
- Location: `automation/test_generator.py` (standalone script) and optional task wrapper `automation/tasks/test_generator.py`.
- Inputs (via `context.extra_data`): `source_file`, `overwrite: bool`
- Output: writes a `tests/test_<module>.py` file.

YAML example (`automation/config/automation_config.yaml`):
```yaml
tasks:
  - module: automation.tasks.test_generator
    name: Generate Tests
    params:
      source_file: app/domains/science/science_module.py
      overwrite: false
```

Pre‑commit hook (ensures no new modules without tests):
```yaml
# .pre-commit-config.yaml (add under repo: local)
- repo: local
  hooks:
    - id: ensure-tests-exist
      name: Ensure tests exist for new modules
      entry: python automation/check_test_coverage.py
      language: python
      pass_filenames: false
      always_run: true
```

Related script (already in your blueprint): `automation/check_test_coverage.py`.

### 3.2 API documentation sync (critical)
- Purpose: eliminate drift; generate docs from FastAPI OpenAPI.
- Task path: `automation/tasks/sync_api_docs.py`
- Logic: import `app.main:app`, call `app.openapi()`, write `docs/API_REFERENCE.md` (human‑friendly) and `docs/openapi.json`.
- Inputs: `output_json`, `output_md` (defaults shown below)

YAML example:
```yaml
tasks:
  - module: automation.tasks.sync_api_docs
    name: Sync API Docs
    params:
      output_json: docs/openapi.json
      output_md: docs/API_REFERENCE.md
```

Pre‑commit (run on every commit):
```yaml
- repo: local
  hooks:
    - id: sync-api-docs
      name: Sync API Docs from FastAPI
      entry: python -m automation.scripts.run_automation --task Sync API Docs --dry-run false
      language: system
      pass_filenames: false
```

### 3.3 Endpoint smoke tests (high)
- Purpose: protect against wiring/regression errors across domains.
- Task path: `automation/tasks/smoke_test_endpoints.py`
- Logic: use `httpx`/`requests` TestClient (or live URL) to hit key endpoints.
- Inputs: `base_url` (optional; if omitted, use TestClient on `app.main.app`).
- Fail fast on non‑200.

YAML example:
```yaml
tasks:
  - module: automation.tasks.smoke_test_endpoints
    name: Smoke Test Endpoints
    params:
      base_url: null  # use TestClient if null
```

Recommended URIs to cover now:
- `POST /api/science/biomedical/search`
- `POST /api/commerce/ubi/simulate`
- `POST /api/arts/create`
- `POST /api/finance/personal/analyze`
- `GET /api/health`, `GET /api/metrics`

### 3.4 Dependency update + audit (high)
- Purpose: keep libs fresh and safe.
- Task path: `automation/tasks/deps_update.py`
- Logic: run `pip list --outdated` (or `pip-tools` if adopted), open PR with updates.
- Integrate `pip-audit` (or `safety`) and attach report to PR.

YAML example:
```yaml
tasks:
  - module: automation.tasks.deps_update
    name: Update Dependencies
    params:
      audit: true
```

CI schedule (weekly): see §4.2.

### 3.5 Security scans (high)
- Purpose: early signal on vulnerable code & packages.
- Task path: `automation/tasks/security_scan.py`
- Logic: run `bandit -q -r app automation packages`, `pip-audit -r requirements.txt`; write combined report under `automation/reports/security/` and fail CI on high severity.

YAML example:
```yaml
tasks:
  - module: automation.tasks.security_scan
    name: Security Scan
    params:
      fail_on: high
```

### 3.6 Release notes generation (medium)
- Purpose: ship logs with structure.
- Task path: `automation/tasks/release_notes.py`
- Logic: parse Conventional Commits or PR titles; output `RELEASE_NOTES.md` grouped by feat/fix/chore.

YAML example:
```yaml
tasks:
  - module: automation.tasks.release_notes
    name: Generate Release Notes
    params:
      since_tag: v0.1.0
      out_file: RELEASE_NOTES.md
```

### 3.7 Performance benchmarking (medium)
- Purpose: detect perf regressions.
- Task path: `automation/tasks/perf_bench.py`
- Logic: use `pytest-benchmark` or simple timers; run critical flows; store to `automation/reports/perf/*.json`; compare to last known baseline and fail CI on +N%.

YAML example:
```yaml
tasks:
  - module: automation.tasks.perf_bench
    name: Performance Benchmark
    params:
      threshold_percent: 20
```

---

## 4) Wiring: Runner, Pre‑commit, and CI

### 4.1 Runner usage
```
# Dry run (safety)
python -m automation.scripts.run_automation --task "Sync API Docs" --dry-run true

# Execute
automation/scripts/run_automation.py --task "Sync API Docs"
```

Ensure `run_automation.py` supports `--task` selection and passes `params` to `Context.extra_data` (it currently wires frequency/type; extend as needed).

### 4.2 GitHub Actions
Create `.github/workflows/ci.yml`:
- **jobs**: lint (black/flake8/mypy), unit tests (pytest), smoke (automation smoke test), docs (Sync API Docs, upload artifact)

Create `.github/workflows/weekly.yml` (cron):
- **jobs**: deps update (+ pip‑audit), security scan, performance benchmark, release notes draft

Cache `pip` and test artifacts; upload `automation/reports/*` as workflow artifacts.

---

## 5) Environment & Safety

- Add `./.env.example`:
  - `SECRET_KEY=change_me_in_production`
  - `HOST=127.0.0.1`
  - `PORT=8000`
  - `LOG_LEVEL=info`
  - `RELOAD=true`
- `app/core/auth.py` should read `SECRET_KEY` from env in production.
- All tasks must respect `Context.dry_run` and use `Context.require_confirmation()` before mutating operations (e.g., writing large files, opening PRs, mass renames).

---

## 6) Documentation & Status Sync

Update to reflect actual implemented domains (now wired in `app/main.py`):
- Science: `/biomedical/search`, `/chemistry/simulate`, `/physics/simulate`
- Commerce: `/ubi/simulate`, `/employment/match`, `/economy/forecast`
- Arts: `/create`, `/analyze/cultural`, `/language/preserve`, `/history/analyze`
- FinanceAdvisor: `/api/finance/*` routes (`personal/analyze`, `enterprise/analyze`, `prediction/*`, `portfolio/optimize`, `scenario/investment`, `health`)

Have the **Sync API Docs** task regenerate `docs/API_REFERENCE.md` and `docs/openapi.json` on every commit.

---

## 7) Developer Workflow (fast path)

1. **Write code** (feature)
2. **Generate tests**
   - `python automation/test_generator.py app/<path>.py`
3. **Run automation smoke tests**
   - `python -m automation.scripts.run_automation --task "Smoke Test Endpoints"`
4. **Commit**
   - Pre‑commit runs: format, lint, mypy, bandit, ensure‑tests‑exist, sync‑api‑docs
5. **CI** runs full pipeline (tests + docs + reports)
6. **Deploy** (container or PaaS) – API not suited to Netlify; keep Netlify for static docs only.

---

## 8) Task Stubs Summary (what to add)

Create these minimal task files under `automation/tasks/`:
- `test_generator.py` → `def generate_tests(context): ...`
- `sync_api_docs.py` → `def sync_api_docs(context): ...`
- `smoke_test_endpoints.py` → `def smoke_test_endpoints(context): ...`
- `deps_update.py` → `def update_dependencies(context): ...`
- `security_scan.py` → `def security_scan(context): ...`
- `release_notes.py` → `def generate_release_notes(context): ...`
- `perf_bench.py` → `def performance_benchmark(context): ...`

Name each task function exactly as Orchestrator expects (snake‑case of `name` in YAML).

---

## 9) Quick Wins Checklist

- **[ ]** Add `.env.example` and wire `SECRET_KEY` from env
- **[ ]** Add task stubs listed in §8
- **[ ]** Update `automation/config/automation_config.yaml` with tasks
- **[ ]** Extend `.pre-commit-config.yaml` with `ensure-tests-exist` and `sync-api-docs`
- **[ ]** Add CI workflows (`ci.yml`, `weekly.yml`)
- **[ ]** Run first full automation cycle and review `automation/reports/`

---

## 10) Appendix: Notes on Your Framework

- Orchestrator computes `func_name` from `task['name']` (`lower().replace(' ', '_')`). Ensure module defines that function.
- `Context.extra_data` receives params from YAML – read inputs from there in each task.
- Use `AutomationLogger` for consistent logs; prefer `log.info()` and structured messages.

This playbook is designed to slot into your current repo with minimal friction and maximum leverage. Install sections §3.1–§3.3 today for immediate gains; schedule §3.4–§3.7 in weekly CI. 🚀
