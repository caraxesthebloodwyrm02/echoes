# Repository layout and recommended workflow

Top-level layout (what we now expect and maintain):

- `python/` — FastAPI service and Python helpers
  - `service.py` — POST /transform implementation
  - `requirements.txt`, `README.md`, `.venv` (local)

- `csharp/` — C# runner (keeps language-bundle runner and csproj files)

- `tools/` — developer tooling and diagnostics
  - `purge_repo_mirror.ps1` — mirror+purge helper for removing secrets from history
  - `collect_copilot_logs.ps1`, `check_copilot_and_inline.ps1`, `purge_env_history.ps1`

- `.github/workflows/` — CI jobs (integration-windows.yml runs the deterministic integration test)
- `integration_test.ps1` — idempotent integration test used by CI and locally
- `.env.example` and `.gitignore` — guidance to avoid committing secrets

Recommended workflows
- Local development: see `python/README.md` to run the service locally.
- Deterministic E2E test: `.	egration_test.ps1` runs uvicorn with `OPENAI_API_KEY` unset and verifies the local fallback.
- Remove leaked secrets: use `tools/purge_repo_mirror.ps1` (dry-run prints commands; use -Execute to run).
