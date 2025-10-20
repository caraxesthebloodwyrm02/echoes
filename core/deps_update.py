# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Dependency update + audit.
Task name: "Update Dependencies" -> function: update_dependencies(context)
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from automation.core.logger import AutomationLogger


def update_dependencies(context):
    log = AutomationLogger()
    reports_dir = Path("automation/reports/deps")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Check outdated
    try:
        proc = subprocess.run(
            ["pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            log.warning("pip list --outdated failed")
            return
        outdated = json.loads(proc.stdout or "[]")
    except Exception as e:
        log.error(f"Failed to check outdated deps: {e}")
        return

    with open(reports_dir / "outdated.json", "w", encoding="utf-8") as f:
        json.dump(outdated, f, indent=2)
    log.info(f"📦 Outdated packages: {len(outdated)} (saved to reports)")

    if context.dry_run or not context.extra_data.get("apply", False):
        log.info("[DRY-RUN] Skipping requirements update. Run with apply=true to modify.")
        return

    # Update requirements.txt in-place for pinned lines
    req = Path("requirements.txt")
    if not req.exists():
        log.warning("requirements.txt not found; skipping update")
        return
    lines = req.read_text(encoding="utf-8").splitlines()
    name_to_latest = {p["name"].lower(): p["latest_version"] for p in outdated}
    new_lines = []
    for line in lines:
        stripped = line.strip()
        lower = stripped.split("==")[0].lower() if "==" in stripped else stripped.lower()
        if lower in name_to_latest and "==" in stripped:
            new = f"{lower}=={name_to_latest[lower]}"
            new_lines.append(new)
        else:
            new_lines.append(line)
    req.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    log.info("✅ requirements.txt updated; please run pip install -r requirements.txt")
