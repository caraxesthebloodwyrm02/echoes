# HarmonyHub Diff — Quickstart Demo

## Purpose
Small, deterministic diff utility to compare two structured payloads: `harmony` and `melody` @e:\Projects\Development\phase2_demo_report.json.

## Quickstart
1. Windows PowerShell (recommended on Windows):
   ```powershell
   # Run demo (module-based invocation inside the script)
   .\cli\examples.ps1

   # Run tests
   python -m pytest -q
   ```

2. POSIX/macOS (Bash):
   ```bash
   chmod +x cli/examples.sh
   ./cli/examples.sh

   python -m pytest -q
   ```

## Config
See `configs/integration_examples.yaml` for example CLI invocations. `--epsilon` controls numeric tolerance.

## Notes
- Lists compared by index.
- Dict keys are compared structurally.
- Deterministic JSON output uses sorted keys.

---

### Optional `.pending` minimal metadata (demo)
`.pending/phase2_demo_report.json`
```json
{
  "files_added": [
    "app/harmony/diff_service.py",
    "app/harmony/cli.py",
    "configs/integration_examples.yaml",
    "cli/examples.sh",
    "tests/unit/test_diff_core.py",
    "tests/integration/test_diff_cli.py",
    "tests/fixtures/harmony_finance.json",
    "tests/fixtures/melody_finance.json",
    "tests/fixtures/harmony_arts.json",
    "tests/fixtures/melody_arts.json",
    "docs/HARMONYHUB_DIFF.md"
  ],
  "pytest_result": {"exit_code": null, "output": null},
  "ready_for_commit": false,
  "notes": "Local demo scaffold. Run pytest to populate results and flip ready_for_commit true."
}
```

## Run commands (copy-paste)
Windows PowerShell
```powershell
./cli/examples.ps1
python -m pytest -q
```

POSIX/macOS
```bash
chmod +x cli/examples.sh
./cli/examples.sh
python -m pytest -q
```

### Troubleshooting
- If you see `ModuleNotFoundError: No module named 'app'` when running directly via a file path, prefer module invocation: `python -m app.harmony.cli ...`.
