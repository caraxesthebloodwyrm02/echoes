"""
Graph Compiler: transforms CrossReferenceSystem context output into Glimpse Entity shape.

Bridges Echoes' untyped analysis dict into the typed Entity contract that Glimpse's
pipeline expects (core/contracts.js). Emits dual-key fields (camelCase + snake_case)
required by Glimpse's createEvaluationContext / entity construction paths.
"""

from __future__ import annotations

from datetime import UTC, datetime


def _stable_id(name: str) -> str:
    slug = name.lower().strip().replace(" ", "-").replace("_", "-")[:40]
    return f"e-{slug}"


_COMPLEXITY_SCORES = {"high": 1.0, "medium": 0.5, "low": 0.2}


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
        entities.append({
            "id": _stable_id(domain_name),
            "name": domain_name,
            "type": "domain",
            "dimensions": {"time": ts, "space": None, "domain": domain_name, "catalyst": None},
            "metrics": {},
            "domainKeywordHits": domain_hits,
            "domain_keyword_hits": domain_hits,
            "tones": {},
            "tone_hits": {},
        })

    for concept in context_output.get("key_concepts", []):
        concept_lower = concept.lower()
        concept_hits = {d: (1 if d.lower() in concept_lower else 0) for d in domains}
        tone_data = {"sentiment": sentiment}
        entities.append({
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
        })

    for rel in context_output.get("relationships", []):
        rel_domains = rel.get("domains", [])
        rel_name = " + ".join(rel_domains) if rel_domains else rel.get("type", "relation")
        rel_hits = {d: 1 for d in rel_domains}
        entities.append({
            "id": _stable_id(f"rel-{rel_name}"),
            "name": rel_name,
            "type": "relation_node",
            "dimensions": {"time": ts, "space": None, "domain": None, "catalyst": None},
            "metrics": {"complexity": complexity_score},
            "domainKeywordHits": rel_hits,
            "domain_keyword_hits": rel_hits,
            "tones": {},
            "tone_hits": {},
        })

    return entities


_ENTITY_REQUIRED_KEYS = {"id", "name", "type", "dimensions", "domainKeywordHits", "domain_keyword_hits", "tones", "tone_hits"}


def validate_entities(entities: list[dict]) -> list[str]:
    """Check compiled entities against Glimpse Entity contract. Returns error list."""
    errors = []
    for i, e in enumerate(entities):
        missing = _ENTITY_REQUIRED_KEYS - set(e.keys())
        if missing:
            errors.append(f"entity[{i}] missing keys: {missing}")
        if e.get("domainKeywordHits") != e.get("domain_keyword_hits"):
            errors.append(f"entity[{i}] dual-key mismatch: domainKeywordHits != domain_keyword_hits")
        if not isinstance(e.get("id", ""), str) or not e.get("id", "").startswith("e-"):
            errors.append(f"entity[{i}] id must be a string starting with 'e-'")
    return errors
