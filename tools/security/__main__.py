"""CLI for advanced security routine (detect / redact)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.security.advanced_routine import RoutineMode, detect_findings, redact_text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Heuristic secret detection and PII masking (advanced routine).",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files to scan (stdin used if empty and not tty)",
    )
    parser.add_argument(
        "--mode",
        choices=[m.value for m in RoutineMode],
        default=RoutineMode.ADVANCED.value,
    )
    parser.add_argument(
        "--detect-only",
        action="store_true",
        help="Emit JSON findings instead of redacted text",
    )
    args = parser.parse_args()
    mode = RoutineMode(args.mode)

    if args.paths:
        for p in args.paths:
            path = Path(p)
            if not path.is_file():
                print(f"error: not a file or path does not exist: {p}", file=sys.stderr)
                print(
                    "hint: create the file, use an existing path, or pipe stdin "
                    "(e.g. echo 'text' | uv run python -m tools.security --detect-only)",
                    file=sys.stderr,
                )
                sys.exit(2)
            text = path.read_text(encoding="utf-8", errors="replace")
            if args.detect_only:
                findings = detect_findings(text, mode)
                payload = {
                    "path": p,
                    "count": len(findings),
                    "findings": [
                        {"category": f.category, "start": f.start, "end": f.end, "preview": f.mask_preview}
                        for f in findings
                    ],
                }
                print(json.dumps(payload, indent=2))
            else:
                sys.stdout.write(redact_text(text, mode))
        return

    text = sys.stdin.read()
    if args.detect_only:
        findings = detect_findings(text, mode)
        print(
            json.dumps(
                [
                    {"category": f.category, "start": f.start, "end": f.end, "preview": f.mask_preview}
                    for f in findings
                ],
                indent=2,
            )
        )
    else:
        sys.stdout.write(redact_text(text, mode))


if __name__ == "__main__":
    main()
