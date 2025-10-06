"""
Release notes generation from git log.
Task name: "Generate Release Notes" -> function: generate_release_notes(context)
"""
from __future__ import annotations
from pathlib import Path
import subprocess
from datetime import datetime
from automation.core.logger import AutomationLogger


def generate_release_notes(context):
    log = AutomationLogger()
    since = context.extra_data.get("since_tag")
    args = ["git", "log", "--pretty=format:%H|%s|%an|%ad", "--date=short"]
    if since:
        args = ["git", "log", f"{since}..HEAD", "--pretty=format:%H|%s|%an|%ad", "--date=short"]

    try:
        proc = subprocess.run(args, capture_output=True, text=True)
        if proc.returncode != 0:
            log.warning("git log failed; are you in a git repo?")
            return
        lines = [l for l in proc.stdout.splitlines() if l]
    except Exception as e:
        log.error(f"Unable to read git log: {e}")
        return

    def clean_subject(s: str) -> str:
        for p in ["feat:", "fix:", "docs:", "test:", "refactor:", "perf:", "chore:"]:
            if s.lower().startswith(p):
                return s[len(p):].strip()
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
