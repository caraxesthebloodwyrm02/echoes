"""
Advanced routine: heuristic secret detection + PII masking + structured log sanitization.

For telemetry, audit trails, and pre-commit-style scans. Not a substitute for
TruffleHog/gitleaks or full DLP — combines fast regex + Luhn for card-shaped digits.

Modes:
  standard — common API key shapes, Bearer, email, US phone, SSN pattern
  advanced — + JWT-shaped blobs, URL userinfo, GitHub/Stripe/Slack/AWS, private IPv4
  paranoid — + mask all IPv4 (use sparingly; noisy in infrastructure logs)
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any


class RoutineMode(StrEnum):
    STANDARD = "standard"
    ADVANCED = "advanced"
    PARANOID = "paranoid"


@dataclass(frozen=True, slots=True)
class Finding:
    """A detected span (for auditing / counts; snippet is never full secret)."""

    category: str
    start: int
    end: int
    mask_preview: str  # e.g. "sk-…abc" or "<email>"


def _luhn_valid(digits: str) -> bool:
    if len(digits) < 13 or len(digits) > 19:
        return False
    nums = [int(c) for c in digits]
    checksum = 0
    for i, d in enumerate(reversed(nums)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def _mask_preview(raw: str, prefix: int = 4, suffix: int = 3) -> str:
    t = raw.strip()
    if len(t) <= prefix + suffix + 2:
        return "<redacted>"
    return f"{t[:prefix]}…{t[-suffix:]}"


def _compile_patterns(
    mode: RoutineMode,
) -> list[tuple[str, int, re.Pattern[str], Callable[[re.Match[str]], str]]]:
    """
    Return list of (category, priority, pattern, replacer).
    Higher priority wins on overlap; replacer receives match and returns replacement.
    """
    pats: list[tuple[str, int, re.Pattern[str], Callable[[re.Match[str]], str]]] = []

    # --- Secrets / credentials (high priority) ---
    pats.append(
        (
            "openai_sk",
            100,
            re.compile(r"\bsk-(?:proj-)?[a-zA-Z0-9]{10,}\b"),
            lambda _m: "[REDACTED:openai_key]",
        )
    )
    pats.append(
        (
            "bearer",
            98,
            re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]+=*\b"),
            lambda m: "[REDACTED:bearer]",
        )
    )
    pats.append(
        (
            "aws_key",
            95,
            re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"),
            lambda m: "[REDACTED:aws_access_key]",
        )
    )
    pats.append(
        (
            "github_pat",
            93,
            re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
            lambda m: "[REDACTED:github_token]",
        )
    )
    pats.append(
        (
            "stripe",
            92,
            re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{10,}\b"),
            lambda m: "[REDACTED:stripe]",
        )
    )
    pats.append(
        (
            "slack_token",
            90,
            re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
            lambda m: "[REDACTED:slack]",
        )
    )
    pats.append(
        (
            "url_credentials",
            88,
            re.compile(r"//[^\s/]+?:[^\s/]+?@[^\s]+"),
            lambda m: "[REDACTED:url_userinfo]",
        )
    )
    pats.append(
        (
            "assign_secret",
            70,
            re.compile(
                r"(?i)\b(?:API_KEY|SECRET|TOKEN|PASSWORD|OPENAI_API_KEY|JWT_SECRET)"
                r"\s*=\s*[^\s#;,\]]+"
            ),
            lambda m: "[REDACTED:assignment]",
        )
    )

    if mode in (RoutineMode.ADVANCED, RoutineMode.PARANOID):
        pats.append(
            (
                "jwt_shape",
                85,
                re.compile(
                    r"\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b",
                ),
                lambda m: "[REDACTED:jwt_like]",
            )
        )

    # --- PII ---
    pats.append(
        (
            "email",
            65,
            re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            ),
            lambda m: "[REDACTED:email]",
        )
    )
    pats.append(
        (
            "us_phone",
            62,
            re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
            lambda m: "[REDACTED:phone]",
        )
    )
    pats.append(
        (
            "ssn",
            64,
            re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            lambda m: "[REDACTED:ssn_pattern]",
        )
    )

    # Credit-card-shaped runs (Luhn); keep only if digits length 13-19
    def cc_replace(m: re.Match[str]) -> str:
        digits = re.sub(r"\D", "", m.group(0))
        if _luhn_valid(digits):
            return "[REDACTED:payment_card]"
        return m.group(0)

    pats.append(
        (
            "card_luhn",
            63,
            re.compile(
                r"\b(?:\d[ -]*?){12,18}\d\b",
            ),
            cc_replace,
        )
    )

    if mode in (RoutineMode.ADVANCED, RoutineMode.PARANOID):
        pats.append(
            (
                "ipv4_private",
                45,
                re.compile(
                    r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
                    r"127\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
                    r"192\.168\.\d{1,3}\.\d{1,3}|"
                    r"172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"
                ),
                lambda m: "[REDACTED:ipv4_private]",
            )
        )

    if mode == RoutineMode.PARANOID:
        pats.append(
            (
                "ipv4_any",
                40,
                re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d{1,2})\b"),
                lambda m: "[REDACTED:ipv4]",
            )
        )

    return pats


def _collect_matches(
    text: str,
    mode: RoutineMode,
) -> list[tuple[int, int, int, str, Callable[[re.Match[str]], str], re.Match[str]]]:
    """Build candidate matches: start, end, priority, category, replacer, match object."""
    out: list[tuple[int, int, int, str, Callable[[re.Match[str]], str], re.Match[str]]] = []
    for category, priority, rx, replacer in _compile_patterns(mode):
        out.extend(
            (m.start(), m.end(), priority, category, replacer, m) for m in rx.finditer(text)
        )
    return out


def _select_non_overlapping(
    raw: list[tuple[int, int, int, str, Callable[[re.Match[str]], str], re.Match[str]]],
) -> list[tuple[int, int, str, Callable[[re.Match[str]], str], re.Match[str]]]:
    """Greedy: sort by (-priority, -length, start); drop overlaps."""
    raw.sort(key=lambda t: (-t[2], -(t[1] - t[0]), t[0]))
    chosen: list[tuple[int, int, str, Callable[[re.Match[str]], str], re.Match[str]]] = []
    for start, end, _prio, cat, replacer, m in raw:
        if any(not (end <= s or start >= e) for s, e, *_ in chosen):
            continue
        chosen.append((start, end, cat, replacer, m))
    chosen.sort(key=lambda t: t[0])
    return chosen


def redact_text(text: str, mode: RoutineMode = RoutineMode.ADVANCED) -> str:
    """Mask secrets and PII; overlapping spans resolved by priority."""
    if not text:
        return text
    matches = _collect_matches(text, mode)
    selected = _select_non_overlapping(matches)
    out: list[str] = []
    pos = 0
    for start, end, _cat, replacer, m in selected:
        out.append(text[pos:start])
        out.append(replacer(m))
        pos = end
    out.append(text[pos:])
    return "".join(out)


def detect_findings(text: str, mode: RoutineMode = RoutineMode.ADVANCED) -> list[Finding]:
    """Non-destructive inventory of spans that would be masked (preview only)."""
    matches = _collect_matches(text, mode)
    selected = _select_non_overlapping(matches)
    findings: list[Finding] = []
    for start, end, cat, _repl, m in selected:
        findings.append(
            Finding(
                category=cat,
                start=start,
                end=end,
                mask_preview=_mask_preview(m.group(0), 3, 2),
            )
        )
    return findings


def sanitize_mapping(
    obj: Any,
    mode: RoutineMode = RoutineMode.ADVANCED,
    *,
    max_depth: int = 6,
    _depth: int = 0,
) -> Any:
    """
    Recursively redact string values in dict/list/tuple structures (e.g. structlog event dict).

    Stops at max_depth; non-serializable values returned as-is.
    """
    if _depth > max_depth:
        return obj
    if isinstance(obj, str):
        return redact_text(obj, mode)
    if isinstance(obj, dict):
        return {k: sanitize_mapping(v, mode, max_depth=max_depth, _depth=_depth + 1) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_mapping(v, mode, max_depth=max_depth, _depth=_depth + 1) for v in obj]
    if isinstance(obj, tuple):
        return tuple(sanitize_mapping(v, mode, max_depth=max_depth, _depth=_depth + 1) for v in obj)
    return obj


def iter_findings_files(
    paths: Iterator[str],
    mode: RoutineMode = RoutineMode.ADVANCED,
    *,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> Iterator[tuple[str, list[Finding]]]:
    """Yield (path, findings) for each file (for repo scans)."""
    for p in paths:
        content = Path(p).read_text(encoding=encoding, errors=errors)
        yield p, detect_findings(content, mode)
