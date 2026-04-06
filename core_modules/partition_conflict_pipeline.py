"""Deterministic partition conflict pipeline for Atlas entities.

Implements Echoes-only event stages:
  conflict_detected -> candidate_scored -> candidate_resolved -> resolution_committed
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

SCOPE_WEIGHTS = {
    "path_space": 2,
    "content_attraction": 1,
}


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _scope_root() -> Path:
    return _repo_root() / "data" / "class-of-21"


def _audit_path() -> Path:
    raw = os.getenv("ECHOES_AUDIT_PATH")
    if raw:
        return Path(raw)
    return Path.home() / ".echoes" / "audit.ndjson"


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=True, sort_keys=True) + "\n")


def emit_event(event: str, payload: dict[str, Any]) -> None:
    entry = {
        "timestamp": _now_iso(),
        "source": "echoes-atlas",
        "tool": "atlas_partition_pipeline",
        "event": event,
        "status": "ok",
        "payload": payload,
    }
    _append_jsonl(_audit_path(), entry)


def _content_confidence(entity: dict[str, Any]) -> float:
    metrics = entity.get("metrics") or {}
    complexity = float(metrics.get("complexity", 0.2) or 0.2)

    domain_hits = entity.get("domainKeywordHits") or {}
    active_domains = sum(1 for v in domain_hits.values() if (v or 0) > 0)
    domain_bonus = min(0.2, active_domains * 0.05)

    return min(1.0, 0.5 + (complexity * 0.3) + domain_bonus)


def _path_confidence(entity: dict[str, Any]) -> float:
    dims = entity.get("dimensions") or {}
    has_space = dims.get("space") not in (None, "", "unknown")
    has_domain = dims.get("domain") not in (None, "", "unknown")

    base = 0.55
    if has_space:
        base += 0.15
    if has_domain:
        base += 0.10
    return min(1.0, base)


def _claims_for_entity(
    conflict_id: str, entity: dict[str, Any], partition_id: str, partition_key: str
) -> list[dict[str, Any]]:
    ts = _now_iso()
    entity_id = entity["id"]

    claims = []
    for claim_kind, confidence in (
        ("path_space", _path_confidence(entity)),
        ("content_attraction", _content_confidence(entity)),
    ):
        claim_id = f"cl-{sha256(f'{conflict_id}:{entity_id}:{claim_kind}'.encode()).hexdigest()[:12]}"
        claims.append(
            {
                "claim_id": claim_id,
                "claim_kind": claim_kind,
                "partition_id": partition_id,
                "partition_key": partition_key,
                "entity_id": entity_id,
                "candidate_id": f"{entity_id}:{claim_kind}",
                "confidence": round(float(confidence), 6),
                "scope_weight": SCOPE_WEIGHTS[claim_kind],
                "provenance": {
                    "source": "atlas_partition_pipeline",
                    "timestamp": ts,
                    "algorithm": "confidence-first-v1",
                },
            }
        )
    return claims


def _select_winner(claims: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    ranked = sorted(
        claims,
        key=lambda c: (
            -float(c["confidence"]),
            -int(c["scope_weight"]),
            str(c["candidate_id"]),
        ),
    )
    return ranked[0], ranked[1:]


def run_conflict_pipeline(conflicts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Resolve conflicts and persist artifacts/events.

    Args:
        conflicts: list with keys partition_id, partition_key, entities
    """
    scope_root = _scope_root()
    resolutions_dir = scope_root / "manifests" / "resolutions"
    resolutions_dir.mkdir(parents=True, exist_ok=True)

    summaries: list[dict[str, Any]] = []

    for conflict in conflicts:
        partition_id = str(conflict["partition_id"])
        partition_key = str(conflict["partition_key"])
        entities = list(conflict.get("entities") or [])

        conflict_id = f"cf-{sha256(f'{partition_id}:{partition_key}'.encode()).hexdigest()[:12]}"
        emit_event(
            "conflict_detected",
            {
                "conflict_id": conflict_id,
                "partition_id": partition_id,
                "partition_key": partition_key,
                "entity_count": len(entities),
            },
        )

        claims: list[dict[str, Any]] = []
        for entity in entities:
            claims.extend(_claims_for_entity(conflict_id, entity, partition_id, partition_key))

        emit_event(
            "candidate_scored",
            {
                "conflict_id": conflict_id,
                "partition_id": partition_id,
                "candidate_count": len(claims),
            },
        )

        winner, losers = _select_winner(claims)

        emit_event(
            "candidate_resolved",
            {
                "conflict_id": conflict_id,
                "partition_id": partition_id,
                "winner_candidate_id": winner["candidate_id"],
            },
        )

        resolution = {
            "resolution_id": f"rs-{sha256((conflict_id + winner['candidate_id']).encode()).hexdigest()[:12]}",
            "conflict_id": conflict_id,
            "partition_id": partition_id,
            "partition_key": partition_key,
            "winner": {
                "candidate_id": winner["candidate_id"],
                "entity_id": winner["entity_id"],
                "claim_kind": winner["claim_kind"],
                "confidence": winner["confidence"],
            },
            "losers": [
                {
                    "candidate_id": c["candidate_id"],
                    "entity_id": c["entity_id"],
                    "claim_kind": c["claim_kind"],
                    "confidence": c["confidence"],
                }
                for c in losers
            ],
            "policy": "confidence-first",
            "tie_breakers": ["scope_weight", "candidate_id_lexical"],
            "timestamp": _now_iso(),
        }

        resolution_path = resolutions_dir / f"{conflict_id}.json"
        with resolution_path.open("w", encoding="utf-8") as f:
            json.dump(resolution, f, ensure_ascii=True, indent=2, sort_keys=True)
            f.write("\n")

        emit_event(
            "resolution_committed",
            {
                "conflict_id": conflict_id,
                "partition_id": partition_id,
                "resolution_path": str(resolution_path),
            },
        )

        summaries.append(
            {
                "conflict_id": conflict_id,
                "partition_id": partition_id,
                "winner_entity_id": winner["entity_id"],
                "winner_candidate_id": winner["candidate_id"],
                "blocked_entity_ids": sorted({c["entity_id"] for c in losers if c["entity_id"] != winner["entity_id"]}),
            }
        )

    return summaries


def apply_resolution_states(entities: list[dict[str, Any]], summaries: list[dict[str, Any]]) -> None:
    """Mutate entities in-place: winners resolved_winner, losers blocked."""
    winner_by_partition = {s["partition_id"]: s["winner_entity_id"] for s in summaries}
    blocked_by_partition = {s["partition_id"]: set(s["blocked_entity_ids"]) for s in summaries}

    for entity in entities:
        pid = entity.get("partition_id")
        if pid in blocked_by_partition and entity.get("id") in blocked_by_partition[pid]:
            entity["conflict_state"] = "blocked"
        elif pid in winner_by_partition and entity.get("id") == winner_by_partition[pid]:
            entity["conflict_state"] = "resolved_winner"


def append_partition_registry(entities: list[dict[str, Any]]) -> Path:
    """Append current entity partition records to the class-of-21 registry.

    Deduplicates: an (entity_id, partition_id) pair that already exists in
    the registry is skipped to prevent re-run bloat.
    """
    registry_path = _scope_root() / "manifests" / "partition_registry.jsonl"

    # Load existing keys for dedup
    existing: set[tuple[str, str]] = set()
    if registry_path.exists():
        for raw in registry_path.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
                existing.add((row.get("entity_id", ""), row.get("partition_id", "")))
            except json.JSONDecodeError:
                continue

    appended = 0
    for entity in entities:
        eid = entity.get("id", "")
        pid = entity.get("partition_id", "")
        if (eid, pid) in existing:
            continue
        entry = {
            "timestamp": _now_iso(),
            "entity_id": eid,
            "partition_id": pid,
            "partition_key": entity.get("partition_key"),
            "conflict_state": entity.get("conflict_state", "clear"),
        }
        _append_jsonl(registry_path, entry)
        existing.add((eid, pid))
        appended += 1

    emit_event("partition_registry_append", {"appended": appended, "skipped_dupes": len(entities) - appended})
    return registry_path
