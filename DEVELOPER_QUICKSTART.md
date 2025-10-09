# Developer quickstart

1) Start the Python service locally

```powershell
cd python
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn service:app --host 127.0.0.1 --port 8000
```

2) Run the deterministic integration test (from repo root)

```powershell
.\integration_test.ps1 -Port 8000
```

3) Run CI on PRs: the workflow `.github/workflows/integration-windows.yml` runs the same integration test on Windows runners.

4) If a `.env` was accidentally committed, use `tools/purge_repo_mirror.ps1` (dry-run) to review commands and `tools/purge_env_history.ps1` for alternative guidance.
