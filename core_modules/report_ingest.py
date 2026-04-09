"""Report staging and deterministic delta proposal/application for class-of-21."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

from core_modules.graph_compiler import detect_partition_conflicts
from core_modules.partition_conflict_pipeline import (
    append_partition_registry,
    apply_resolution_states,
    run_conflict_pipeline,
)


class ReportIngestError(ValueError):
    """Raised when report staging or ingestion fails."""


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _scope_root() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "class-of-21"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2, sort_keys=True)
        f.write("\n")


def _slug(text: str) -> str:
    return "-".join(text.lower().replace("_", "-").split())[:48] or "item"


def _norm_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _partition_key(entity: dict[str, Any]) -> str:
    dims = entity.get("dimensions") or {}
    return "|".join(
        [
            _norm_text(entity.get("type")),
            _norm_text(entity.get("name")),
            _norm_text(dims.get("space")),
            _norm_text(dims.get("domain")),
            _norm_text(dims.get("catalyst")),
        ]
    )


def _partition_id(partition_key: str) -> str:
    return f"p-{sha256(partition_key.encode('utf-8')).hexdigest()[:16]}"


def _fingerprint(entity: dict[str, Any]) -> str:
    raw = json.dumps(entity, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return f"fp-{sha256(raw.encode('utf-8')).hexdigest()[:16]}"


def _attach_partition_metadata(entity: dict[str, Any]) -> dict[str, Any]:
    partition_key = _partition_key(entity)
    entity["partition_key"] = partition_key
    entity["partition_id"] = _partition_id(partition_key)
    entity["payload_fingerprint"] = _fingerprint(entity)
    entity.setdefault("conflict_state", "clear")
    return entity


def stage_report(report_path: str | Path) -> str:
    src = Path(report_path).expanduser().resolve()
    if not src.exists() or not src.is_file():
        raise ReportIngestError(f"report path does not exist: {src}")

    payload = src.read_bytes()
    digest = sha256(payload).hexdigest()
    staged_report_id = f"rp-{digest[:12]}"

    incoming_dir = _scope_root() / "incoming"
    incoming_dir.mkdir(parents=True, exist_ok=True)

    suffix = src.suffix or ".txt"
    staged_path = incoming_dir / f"{staged_report_id}{suffix}"
    if not staged_path.exists():
        staged_path.write_bytes(payload)

    manifest_path = incoming_dir / f"{staged_report_id}.manifest.json"
    if not manifest_path.exists():
        _write_json(
            manifest_path,
            {
                "staged_report_id": staged_report_id,
                "source_path": str(src),
                "staged_path": str(staged_path),
                "sha256": digest,
                "timestamp": _now_iso(),
            },
        )

    return staged_report_id


def _resolve_staged_path(staged_report_id: str) -> Path:
    incoming = _scope_root() / "incoming"
    matches = sorted(incoming.glob(f"{staged_report_id}.*"))
    matches = [m for m in matches if not m.name.endswith(".manifest.json")]
    if not matches:
        raise ReportIngestError(f"No staged report found for id: {staged_report_id}")
    return matches[0]


def _extract_lines_from_markdown(text: str) -> list[str]:
    claims: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(("- ", "* ")):
            claims.append(line[2:].strip())
        elif line[:2].isdigit() and ". " in line[:4]:
            claims.append(line.split(". ", 1)[1].strip())
    return claims


def extract_claims(staged_report_id: str) -> str:
    staged_path = _resolve_staged_path(staged_report_id)
    text = staged_path.read_text(encoding="utf-8", errors="replace")

    claims: list[dict[str, Any]] = []
    parsed = None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None

    if isinstance(parsed, dict) and isinstance(parsed.get("claims"), list):
        for idx, item in enumerate(parsed["claims"], start=1):
            if isinstance(item, str):
                claims.append({"claim_id": f"{staged_report_id}-c{idx:03d}", "text": item.strip()})
            elif isinstance(item, dict):
                claim_text = str(item.get("text", "")).strip()
                if claim_text:
                    claims.append(
                        {
                            "claim_id": str(item.get("claim_id", f"{staged_report_id}-c{idx:03d}")),
                            "text": claim_text,
                            "kind": str(item.get("kind", "content_attraction")),
                            "domain": str(item.get("domain", "report")),
                        }
                    )
    elif isinstance(parsed, list):
        for idx, item in enumerate(parsed, start=1):
            if isinstance(item, str) and item.strip():
                claims.append({"claim_id": f"{staged_report_id}-c{idx:03d}", "text": item.strip()})
    else:
        for idx, claim in enumerate(_extract_lines_from_markdown(text), start=1):
            claims.append({"claim_id": f"{staged_report_id}-c{idx:03d}", "text": claim})

    if not claims:
        claims = [{"claim_id": f"{staged_report_id}-c001", "text": text.strip()[:400] or "empty-report"}]

    output_path = _scope_root() / "quarantine" / f"{staged_report_id}.claims.json"
    _write_json(
        output_path,
        {
            "staged_report_id": staged_report_id,
            "claim_count": len(claims),
            "claims": claims,
            "timestamp": _now_iso(),
        },
    )
    return str(output_path)


def _claim_to_delta(claim: dict[str, Any]) -> dict[str, Any]:
    claim_id = (
        str(claim.get("claim_id", "")).strip()
        or f"cl-{sha256(json.dumps(claim, sort_keys=True).encode()).hexdigest()[:10]}"
    )
    text = str(claim.get("text", "")).strip() or "unspecified claim"
    kind = str(claim.get("kind", "content_attraction")).strip() or "content_attraction"
    if kind not in {"path_space", "content_attraction"}:
        kind = "content_attraction"

    domain = str(claim.get("domain", "report")).strip() or "report"
    name = text[:72]
    entity = {
        "id": f"e-{_slug(claim_id)}",
        "name": name,
        "type": "report_claim",
        "dimensions": {
            "time": _now_iso(),
            "space": claim.get("path", "/reports/staged"),
            "domain": domain,
            "catalyst": kind,
        },
        "metrics": {
            "complexity": 0.7 if kind == "path_space" else 0.5,
        },
        "domainKeywordHits": {domain: 1},
        "tones": {"source": "report"},
        "claim_id": claim_id,
        "claim_kind": kind,
        "claim_text": text,
    }
    return _attach_partition_metadata(entity)


def propose_deltas(claims_path: str | Path) -> str:
    src = Path(claims_path).expanduser().resolve()
    if not src.exists():
        raise ReportIngestError(f"claims file does not exist: {src}")

    payload = json.loads(src.read_text(encoding="utf-8"))
    claims = payload.get("claims")
    if not isinstance(claims, list):
        raise ReportIngestError("claims payload missing list at key 'claims'")

    candidates = [_claim_to_delta(c) for c in claims]
    output_path = _scope_root() / "quarantine" / f"{src.stem}.delta_candidates.json"
    _write_json(
        output_path,
        {
            "source_claims": str(src),
            "candidate_count": len(candidates),
            "candidates": candidates,
            "timestamp": _now_iso(),
        },
    )
    return str(output_path)


def apply_delta_candidates(delta_candidates_path: str | Path) -> dict[str, Any]:
    src = Path(delta_candidates_path).expanduser().resolve()
    if not src.exists():
        raise ReportIngestError(f"delta candidate file does not exist: {src}")

    payload = json.loads(src.read_text(encoding="utf-8"))
    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        raise ReportIngestError("delta payload missing list at key 'candidates'")

    conflicts = detect_partition_conflicts(candidates)
    summaries = run_conflict_pipeline(conflicts) if conflicts else []
    if summaries:
        apply_resolution_states(candidates, summaries)

    append_partition_registry(candidates)

    active = [c for c in candidates if c.get("conflict_state") != "blocked"]
    blocked = [c for c in candidates if c.get("conflict_state") == "blocked"]

    result = {
        "delta_candidates_path": str(src),
        "active_count": len(active),
        "blocked_count": len(blocked),
        "conflicts_resolved": len(summaries),
        "active_entity_ids": [c.get("id") for c in active],
        "blocked_entity_ids": [c.get("id") for c in blocked],
        "timestamp": _now_iso(),
    }

    apply_path = _scope_root() / "curated" / f"{src.stem}.apply_result.json"
    _write_json(apply_path, result)
    return result
