"""
Semantic Guardrails Automation Task

- Loads allowlist/blacklist from config
- Scans codebase for violations and contextually explains findings
- Uses semantic context (file location, usage, comments, and code relationships)
- Can be run in dry-run (report only) or enforce mode (fail, block, or alert)
- Designed for integration with CI, pre-commit, and weekly automation

Usage:
    python -m automation.scripts.run_automation --task "Semantic Guardrails"

Parameters (context.extra_data):
- dry_run: bool (default True)
- allowlist_path: str
- blacklist_path: str
- fail_on_violation: bool (default False)
- report_file: str
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from automation.core.logger import AutomationLogger


def _load_yaml(path: Path) -> Dict[str, Any]:
    import yaml

    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _scan_codebase(
    root: Path, allow: Dict[str, Any], deny: Dict[str, Any]
) -> Dict[str, Any]:
    violations: List[Dict[str, Any]] = []
    context_hits: List[Dict[str, Any]] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        # Extension-based check
        ext = p.suffix.lower()
        if ext in deny.get("disallowed_extensions", []):
            violations.append(
                {
                    "type": "extension",
                    "file": str(p),
                    "ext": ext,
                    "context": _summarize_context(p),
                }
            )
        # Tool/manifest/pattern checks
        name = p.name
        for pat in deny.get("blacklist_patterns", []):
            if pat in name:
                violations.append(
                    {
                        "type": "pattern",
                        "file": str(p),
                        "pattern": pat,
                        "context": _summarize_context(p),
                    }
                )
        # Content-based check
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for tool in deny.get("disallowed_tools", []):
            if re.search(rf"\b{re.escape(tool)}\b", text):
                violations.append(
                    {
                        "type": "tool",
                        "file": str(p),
                        "tool": tool,
                        "context": _summarize_context(p, text),
                    }
                )
        for lang in deny.get("disallowed_languages", []):
            if re.search(rf"\b{re.escape(lang)}\b", text):
                context_hits.append(
                    {
                        "type": "language",
                        "file": str(p),
                        "lang": lang,
                        "context": _summarize_context(p, text),
                    }
                )
    return {"violations": violations, "context_hits": context_hits}


def _summarize_context(p: Path, text: str = None) -> str:
    """Semantic context: file location, comments, and code relationships."""
    context = f"Location: {p}"
    if text:
        # Extract first comment/docstring or first 10 lines
        lines = text.splitlines()
        comments = [
            line
            for line in lines[:20]
            if line.strip().startswith(("#", "//", "/*", '"""', "'''", "--"))
        ]
        if comments:
            context += "\nComment: " + comments[0]
        else:
            context += "\nExcerpt: " + "\n".join(lines[:5])
    return context


def _write_report(
    report: Dict[str, Any], out_path: Path, log: AutomationLogger
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report_json = json.dumps(report, indent=2, sort_keys=True)
    out_path.write_text(report_json, encoding="utf-8")
    log.info(f"Wrote semantic guardrails report: {out_path}")

    additional_dir = Path(r"E:\Projects\Development\text_reports")
    additional_dir.mkdir(parents=True, exist_ok=True)
    secondary_path = additional_dir / out_path.name
    secondary_path.write_text(report_json, encoding="utf-8")
    log.info(f"Mirrored semantic guardrails report: {secondary_path}")


def semantic_guardrails(context) -> None:
    log = AutomationLogger()
    root = Path(".")
    dry_run = bool(context.extra_data.get("dry_run", True))
    allowlist_path = Path(
        context.extra_data.get(
            "allowlist_path", "automation/config/guardrails_whitelist.yaml"
        )
    )
    blacklist_path = Path(
        context.extra_data.get(
            "blacklist_path", "automation/config/guardrails_blacklist.yaml"
        )
    )
    fail_on_violation = bool(context.extra_data.get("fail_on_violation", False))
    report_file = context.extra_data.get(
        "report_file", "automation/reports/semantic_guardrails_report.json"
    )

    log.info(
        f"Semantic Guardrails: Scanning with allowlist={allowlist_path} blacklist={blacklist_path}"
    )
    allow = _load_yaml(allowlist_path)
    deny = _load_yaml(blacklist_path)
    scan_result = _scan_codebase(root, allow, deny)
    _write_report(scan_result, Path(report_file), log)

    num_viol = len(scan_result["violations"])
    if num_viol:
        log.warning(f"❌ {num_viol} semantic guardrail violations found!")
        for v in scan_result["violations"][:5]:
            log.warning(
                f"- {v['file']} [{v['type']}] {v.get('pattern', v.get('tool', v.get('ext', '')))}"
            )
        if not dry_run and fail_on_violation:
            raise RuntimeError(
                f"Semantic guardrails: {num_viol} violations detected. Failing as requested."
            )
    else:
        log.info("✅ No semantic guardrail violations detected.")

    if scan_result["context_hits"]:
        log.info(
            f"ℹ️  {len(scan_result['context_hits'])} context hits (non-blocking, for review)"
        )
