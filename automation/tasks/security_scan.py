"""
Security scanning wrapper.
Task name: "Security Scan" -> function: security_scan(context)
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from automation.core.logger import AutomationLogger


def _run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        return 127, "", str(e)


def security_scan(context):
    log = AutomationLogger()
    out_dir = Path("automation/reports/security")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Bandit
    code_paths = ["app", "automation", "packages"]
    code_paths = [p for p in code_paths if Path(p).exists()]
    bandit_cmd = [
        "bandit",
        "-q",
        "-r",
        *code_paths,
        "-f",
        "json",
        "-o",
        str(out_dir / "bandit.json"),
    ]
    rc, _, err = _run(bandit_cmd)
    if rc != 0:
        log.warning(f"Bandit skipped or failed (rc={rc}): {err}")
    else:
        log.info("✅ Bandit report written")

    # pip-audit (fallback to safety if needed)
    if Path("requirements.txt").exists():
        rc, out, err = _run(["pip-audit", "-r", "requirements.txt", "-f", "json"])
        if rc == 0 and out:
            (out_dir / "pip-audit.json").write_text(out, encoding="utf-8")
            log.info("✅ pip-audit report written")
        else:
            log.warning(f"pip-audit skipped or failed (rc={rc}): {err}")
    else:
        log.warning("requirements.txt not found; skipping dependency audit")
