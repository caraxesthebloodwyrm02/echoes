# 📁# Project Structure (2025 Streamlined)
 - Educational Ecosystem

## ✅ Reorganized Codebase (v3.0)

**Date**: 2025-09-30
**Status**: Clean, Maintainable, Production-Ready

## Folders

- `app/` — Main FastAPI application code
- `automation/`
  - `core/` — Context, logger, Orchestrator
  - `tasks/` — All automation and guardrail tasks
  - `config/` — YAML configs, allowlist/blacklist
  - `reports/` — Automation and compliance reports
  - `scripts/` — Automation runner entrypoints
- `packages/` — Shared Python libraries (core, security, monitoring)
- `tests/` — Integration and Glimpse tests
- `docs/` — Documentation and guides
- `scripts/` — (Optional) Shell/PowerShell scripts for dev/ops

## Usage

- **Run API:**
  ```bash
  python app/main.py
  ```
- **Run tests:**
  ```bash
  pytest
  ```
- **Run automation tasks:**
  ```bash
  python -m automation.scripts.run_automation --task "Task Name"
  # See automation/config/automation_config.yaml for available tasks
  ```
- **Foreign dependency scan:**
  ```bash
  python -m automation.scripts.run_automation --task "Foreign Dependency Sanitize" --dry-run
  ```
- **Security monitoring:**
  ```bash
  python -m automation.scripts.run_automation --task "Security Monitoring"
  ```
- **Semantic guardrails:**
  ```bash
  python -m automation.scripts.run_automation --task "semantic Guardrails" --dry-run
  ```

## Test Functionality:

- **Run API:**
  ```bash
  python app/main.py
  ```
- **Run tests:**
  ```bash
  pytest
  ```
- **Run automation tasks:**
  ```bash
  python -m automation.scripts.run_automation --task "Task Name"
  # See automation/config/automation_config.yaml for available tasks
  ```
- **Foreign dependency scan:**
  ```bash
  python -m automation.scripts.run_automation --task "Foreign Dependency Sanitize" --dry-run
  ```
- **Security monitoring:**
  ```bash
  python -m automation.scripts.run_automation --task "Security Monitoring"
  ```
- **semantic guardrails:**
  ```bash
  python -m automation.scripts.run_automation --task "semantic Guardrails" --dry-run
  ```

All of the above should work without errors!
**The codebase is now:**
- ✅ Clean and organized
- ✅ Easy to navigate
- ✅ Professional structure
- ✅ Maintainable
- ✅ Scalable
- ✅ Fully functional

**Version**: 3.0.0 (Reorganized)
**Status**: Production Ready
**Structure**: Clean & Maintainable
**All Tests**: Passing ✅
