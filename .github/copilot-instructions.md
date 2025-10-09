## Quick instructions for AI coding agents

This file is a compact, actionable guide to help automated coding assistants (and humans) be productive in this repository.

### Big-picture architecture
- Python FastAPI service at `python/service.py` exposes a single POST /transform endpoint. It prefers an upstream model when `OPENAI_API_KEY` is set; otherwise it uses a deterministic local fallback (returns "[local-echo] <reversed input>").
- A small C# runner (`csharp/Program.cs`) probes the Python service and performs a Java probe (it searches upward for `bin/java.exe` and exits with distinct codes when Java is missing or fails).
- `run_bundle.ps1` is a convenience developer script that orchestrates running the Python service and the C# runner and writes `run.log` for local end-to-end runs.

### Key files and where to look first
- `python/service.py` — service implementation, request/response contract, and local fallback behavior.
- `integration_test.ps1` — deterministic PowerShell integration test that creates/uses `python/.venv`, starts the service (uvicorn), posts `{"text":"abc"}`, and expects `[local-echo] cba` when `OPENAI_API_KEY` is unset.
- `run_bundle.ps1` — developer convenience script for Windows to start both components.
- `csharp/Program.cs` and `language-bundle.csproj` — C# build/run entry; helpful when changing how the runner interacts with the Python service or Java.
- `tools/` — contains diagnostics and maintenance helpers (e.g., `purge_env_history.ps1`, `collect_copilot_logs.ps1`, `check_copilot_and_inline.ps1`).
- CI workflow: `.github/workflows/integration-windows.yml` — shows how the repo runs the deterministic integration test on Windows runners.

### Endpoint contract (use this in tests and examples)
- POST /transform
  - Request JSON: { "text": "<string>" }
  - Local deterministic response when OPENAI_API_KEY is empty: `{"result":"[local-echo] <reversed text>"}`
  - Example: POST {"text":"abc"} -> `"[local-echo] cba"`

### Developer workflows (concrete commands)
- Create venv, install, run service (PowerShell):
  - cd python; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; .\.venv\Scripts\python.exe -m uvicorn service:app --host 127.0.0.1 --port 8000
- Run the deterministic integration test (idempotent): `.\integration_test.ps1` from repo root. It ensures `OPENAI_API_KEY` is unset for deterministic output.
- Build/run C# (from `csharp` folder): `dotnet build` then `dotnet run --project .` (adjust depending on your local layout).
- Full end-to-end (Windows): run `.
un_bundle.ps1` — convenient but opaque; inspect `run.log` for symptoms.

### Project-specific conventions & gotchas
- Python venv: repository expects `python/.venv` for local development; tests and scripts use that path.
- Secrets: `.env` should not be committed. Use `.env.example` and GitHub Actions secrets for real keys. `OPENAI_API_KEY` controls whether the service uses OpenAI or the local fallback.
- Deterministic test behavior: the integration test intentionally unsets `OPENAI_API_KEY` so CI and local runs are reproducible.
- Java probing: `csharp/Program.cs` looks for `bin/java.exe` upwards in the tree. If you add a Java dependency, ensure the runner can find or be configured to point to the binary.
- Exit codes: the C# runner returns distinct exit codes for Java-not-found vs Java-failed — preserve these semantics when changing runner logic.

### Integration points and external dependencies
- OpenAI API: optional; controlled by `OPENAI_API_KEY`. When present the service will call the OpenAI SDK (see `python/service.py`).
- Uvicorn + FastAPI: used to host the Python service.
- dotnet/runtime: required to build/run the C# runner.

### Useful examples for automated edits
- To add a new transform variant, update `python/service.py` and add a new test in `integration_test.ps1` that asserts the expected JSON for the new input.
- To change how the C# runner probes Java, update `csharp/Program.cs` and mirror tests in CI by adding a fake `bin/java.exe` in the runner path for validation.

### Tests, CI and maintenance notes
- CI job `.github/workflows/integration-windows.yml` runs the same PowerShell integration test used locally. Keep the test deterministic by not depending on real API keys.
- Use `tools/purge_env_history.ps1` (dry-run) to produce commands when removing secrets from git history — it will not execute destructive steps unless explicitly invoked.
- For a one-shot mirror+purge helper see `tools/purge_repo_mirror.ps1` (prints commands by default; use -Execute to run). See `REPO_LAYOUT.md` for the recommended repository layout.

If anything in this document is unclear or outdated, tell me which file I should re-scan and I will update these instructions.

### Contract + concrete examples
- Request shape: POST /transform with JSON { "text": "..." }
- Response shape: JSON { "result": "<string>" }
- Local fallback behaviour (as implemented in `python/service.py`): when `OPENAI_API_KEY` is empty the service returns `{"result": "[local-echo] <reversed input>"}`. Example:
  - Request: { "text": "abc" }
  - Response: { "result": "[local-echo] cba" }

### Troubleshooting common failures observed during local runs
- pip access / virtualenv errors: if `pip install` fails with a FileNotFoundError while creating an access-test file, try:
  - ensure Python is installed and available on PATH
  - run the venv creation and pip install steps from an elevated PowerShell if your machine restricts filesystem access
  - manually create a `.venv` and use the system Python if virtualenv creation fails
- uvicorn not found: install `uvicorn[standard]` into the venv (`pip install -r python/requirements.txt`) or run the service with the system `python -m uvicorn` after activating the venv.

### Where to run history-purge helpers
- Use `tools/purge_env_history.ps1` to print recommended commands (dry-run).
- Use `tools/purge_repo_mirror.ps1 -RemoteUrl 'https://github.com/owner/repo.git'` to print a mirror+purge sequence; add `-Execute` only when you are ready to rewrite history and force-push.

### Developer quickstart pointers
- For a compact, copy-paste developer quickstart see `DEVELOPER_QUICKSTART.md` at the repo root.
