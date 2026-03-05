# Path and import setup (Echoes)

## Repo root

- **Canonical location**: `E:\Seeds\echoes` (or set `ECHOES_ROOT` to your clone path).
- **In code**: use `tools.path_setup.REPO_ROOT` or `tools.path_setup.ensure_repo_on_path()` instead of ad-hoc `sys.path.insert(0, ...)`.

## Running scripts and tests

1. **From repo root** (recommended):
   ```bash
   cd E:\Seeds\echoes
   set ECHOES_ROOT=%CD%   # optional; scripts infer from __file__ if unset
   python -m pytest tests/
   python -m api.main
   ```
2. **So imports work**: run from repo root so `api`, `app`, `tools` are on the path. If you run a script under `scripts/` or `examples/`, either:
   - Use `PYTHONPATH=. python scripts/scriptname.py`, or
   - Have the script call `from tools.path_setup import ensure_repo_on_path; ensure_repo_on_path()` at the top (or use `python -m scripts.scriptname` once the package is set up).

## Stale paths (fixed)

Previously, many files used hardcoded `e:/Projects/Echoes` or `D:/...`. Those have been updated to:

- Use `ECHOES_ROOT` (defaulting to repo root derived from `__file__`), or
- Use `_REPO_ROOT` / `REPO_ROOT` from `tools.path_setup` or a local `Path(__file__).resolve().parent...` pattern.

External integration paths (e.g. IMPACT_ANALYTICS, GlimpsePreview, TurboBookshelf) are configurable via env vars; see `misc/integrations/impact_analytics_connector.py` and `misc/integrations/turbo_bridge.py`.

## sys.path.insert usage

Many scripts and tests still contain `sys.path.insert(0, project_root)` or similar. That is acceptable as long as the path is the actual repo root (not a stale path). For new code, prefer:

- Running from repo root with `PYTHONPATH=.`, or
- `from tools.path_setup import ensure_repo_on_path; ensure_repo_on_path()`.

This keeps a single place to change if the repo moves again.
