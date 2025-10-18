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
Release notes generation from git log.
Task name: "Generate Release Notes" -> function: generate_release_notes(context)
"""

from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from automation.core.logger import AutomationLogger


def generate_release_notes(context):
    log = AutomationLogger()
    since = context.extra_data.get("since_tag")
    args = ["git", "log", "--pretty=format:%H|%s|%an|%ad", "--date=short"]
    if since:
        args = [
            "git",
            "log",
            f"{since}..HEAD",
            "--pretty=format:%H|%s|%an|%ad",
            "--date=short",
        ]

    try:
        proc = subprocess.run(args, capture_output=True, text=True)
        if proc.returncode != 0:
            log.warning("git log failed; are you in a git repo?")
            return
        lines = [line for line in proc.stdout.splitlines() if line]
    except Exception as e:
        log.error(f"Unable to read git log: {e}")
        return

    def clean_subject(s: str) -> str:
        for p in ["feat:", "fix:", "docs:", "test:", "refactor:", "perf:", "chore:"]:
            if s.lower().startswith(p):
                return s[len(p) :].strip()
        return s

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md = [f"# Release Notes\n\nGenerated: {ts}\n\n---\n"]
    for line in lines:
        h, subj, author, date = line.split("|", 3)
        md.append(f"- {clean_subject(subj)} ([`{h[:7]}`]) — {date} by {author}")
    out = Path(context.extra_data.get("out_file", "RELEASE_NOTES.md"))
    if context.dry_run:
        log.info(f"[DRY-RUN] Would write release notes to: {out}")
        return
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    log.info(f"✅ Release notes written to {out}")
