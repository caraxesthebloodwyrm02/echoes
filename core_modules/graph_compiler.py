"""
Graph Compiler: transforms CrossReferenceSystem context output into Glimpse Entity shape.

Bridges Echoes' untyped analysis dict into the typed Entity contract that Glimpse's
pipeline expects (core/contracts.js). Emits dual-key fields (camelCase + snake_case)
required by Glimpse's createEvaluationContext / entity construction paths.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from hashlib import sha256


def _stable_id(name: str) -> str:
    slug = name.lower().strip().replace(" ", "-").replace("_", "-")[:40]
    return f"e-{slug}"


def _norm_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _partition_key(entity: dict) -> str:
    """Canonical partition key for deterministic clash detection."""
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


def _partition_id(key: str) -> str:
    return f"p-{sha256(key.encode('utf-8')).hexdigest()[:16]}"


def _payload_fingerprint(entity: dict) -> str:
    payload = {
        "id": entity.get("id"),
        "name": entity.get("name"),
        "type": entity.get("type"),
        "dimensions": entity.get("dimensions") or {},
        "metrics": entity.get("metrics") or {},
        "domainKeywordHits": entity.get("domainKeywordHits") or {},
        "tones": entity.get("tones") or {},
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return f"fp-{sha256(raw.encode('utf-8')).hexdigest()[:16]}"


def _attach_partition_metadata(entity: dict) -> None:
    key = _partition_key(entity)
    entity["partition_key"] = key
    entity["partition_id"] = _partition_id(key)
    entity["payload_fingerprint"] = _payload_fingerprint(entity)
    entity.setdefault("conflict_state", "clear")


_COMPLEXITY_SCORES = {"high": 1.0, "medium": 0.5, "low": 0.2}

# Glimpse Entity contract requires both camelCase and snake_case variants.
# This is the canonical dual-key schema — do not modify without updating Glimpse.
ENTITY_DUAL_KEYS = (
    ("domainKeywordHits", "domain_keyword_hits"),
    ("tones", "tone_hits"),
)


def compile_context_to_entities(
    context_output: dict,
    timestamp: str | None = None,
) -> list[dict]:
    """Convert CrossReferenceSystem.analyze_context() output to Glimpse Entity dicts.

    Args:
        context_output: Dict with keys: domains, key_concepts, relationships,
                        complexity, sentiment (from CrossReferenceSystem.analyze_context)
        timestamp: Optional ISO timestamp for the time dimension.

    Returns:
        List of dicts conforming to Glimpse Entity contract. Each dict carries both
        camelCase and snake_case variants of keyword/tone fields.
    """
    entities: list[dict] = []
    ts = timestamp or datetime.now(UTC).isoformat()
    domains = context_output.get("domains", [])
    sentiment = context_output.get("sentiment", "neutral")
    complexity = context_output.get("complexity", "low")
    complexity_score = _COMPLEXITY_SCORES.get(complexity, 0.2)

    for domain_name in domains:
        domain_hits = {domain_name: 1}
        entity = {
            "id": _stable_id(domain_name),
            "name": domain_name,
            "type": "domain",
            "dimensions": {"time": ts, "space": None, "domain": domain_name, "catalyst": None},
            "metrics": {},
            "domainKeywordHits": domain_hits,
            "domain_keyword_hits": domain_hits,
            "tones": {},
            "tone_hits": {},
        }
        _attach_partition_metadata(entity)
        entities.append(entity)

    for concept in context_output.get("key_concepts", []):
        concept_lower = concept.lower()
        concept_hits = {d: (1 if d.lower() in concept_lower else 0) for d in domains}
        tone_data = {"sentiment": sentiment}
        entity = {
            "id": _stable_id(concept),
            "name": concept,
            "type": "concept",
            "dimensions": {
                "time": ts,
                "space": None,
                "domain": domains[0] if domains else None,
                "catalyst": None,
            },
            "metrics": {"complexity": complexity_score},
            "domainKeywordHits": concept_hits,
            "domain_keyword_hits": concept_hits,
            "tones": tone_data,
            "tone_hits": tone_data,
        }
        _attach_partition_metadata(entity)
        entities.append(entity)

    for rel in context_output.get("relationships", []):
        rel_domains = rel.get("domains", [])
        rel_name = " + ".join(rel_domains) if rel_domains else rel.get("type", "relation")
        rel_hits = dict.fromkeys(rel_domains, 1)
        entity = {
            "id": _stable_id(f"rel-{rel_name}"),
            "name": rel_name,
            "type": "relation_node",
            "dimensions": {"time": ts, "space": None, "domain": None, "catalyst": None},
            "metrics": {"complexity": complexity_score},
            "domainKeywordHits": rel_hits,
            "domain_keyword_hits": rel_hits,
            "tones": {},
            "tone_hits": {},
        }
        _attach_partition_metadata(entity)
        entities.append(entity)

    return entities


_ENTITY_REQUIRED_KEYS = {
    "id",
    "name",
    "type",
    "dimensions",
    "metrics",
    "partition_key",
    "partition_id",
    "payload_fingerprint",
    "conflict_state",
    *(k for pair in ENTITY_DUAL_KEYS for k in pair),
}


def validate_entities(entities: list[dict]) -> list[str]:
    """Check compiled entities against Glimpse Entity contract. Returns error list."""
    errors = []
    for i, e in enumerate(entities):
        missing = _ENTITY_REQUIRED_KEYS - set(e.keys())
        if missing:
            errors.append(f"entity[{i}] missing keys: {missing}")
        for camel, snake in ENTITY_DUAL_KEYS:
            if e.get(camel) != e.get(snake):
                errors.append(f"entity[{i}] dual-key mismatch: {camel} != {snake}")
        if not isinstance(e.get("id", ""), str) or not e.get("id", "").startswith("e-"):
            errors.append(f"entity[{i}] id must be a string starting with 'e-'")
        if not isinstance(e.get("partition_id", ""), str) or not e.get("partition_id", "").startswith("p-"):
            errors.append(f"entity[{i}] partition_id must be a string starting with 'p-'")
        if e.get("conflict_state") not in {"clear", "blocked", "resolved_winner"}:
            errors.append(f"entity[{i}] conflict_state invalid: {e.get('conflict_state')}")
    return errors


def detect_partition_conflicts(entities: list[dict]) -> list[dict]:
    """Return deterministic partition conflicts where same partition has mismatched payloads."""
    by_partition: dict[str, list[dict]] = {}
    for entity in entities:
        pid = str(entity.get("partition_id", ""))
        if not pid:
            continue
        by_partition.setdefault(pid, []).append(entity)

    conflicts: list[dict] = []
    for partition_id, grouped in by_partition.items():
        if len(grouped) < 2:
            continue
        fingerprints = {str(e.get("payload_fingerprint", "")) for e in grouped}
        if len(fingerprints) <= 1:
            continue

        partition_key = str(grouped[0].get("partition_key", ""))
        conflicts.append(
            {
                "partition_id": partition_id,
                "partition_key": partition_key,
                "entities": sorted(grouped, key=lambda e: str(e.get("id", ""))),
            }
        )
    return sorted(conflicts, key=lambda c: (c["partition_id"], c["partition_key"]))
