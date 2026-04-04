# Atlas Implementation Guide

Instructional reference for building the Atlas knowledge-graph layer across Echoes and Glimpse.
Grounded in transformer research patterns, local research assets, and the four-layer schema
defined in `atlas_schema.md`.

## Purpose

Unify scattered code symbols into a coherent real-time knowledge-graph architecture that
addresses safety, entity recognition, and dimensional + temporal awareness within the data flow.

## Local Asset Inventory

Before writing new code, know what already exists and where.

### Entity and Graph Primitives

| Symbol | Location | Role |
|--------|----------|------|
| `KnowledgeNode(id, type, properties, created_at)` | `canopy/echoes/knowledge_graph.py` | In-memory graph node (mock KG) |
| `KnowledgeRelation(source_id, target_id, relation_type, properties)` | same | Edge type |
| `MemoryFragment(id, content, embedding, metadata)` | same | Embedding-carrying memory unit |
| `Entity(id, name, type, dimensions, metrics, evidenceIds)` | `glimpse-engine/core/contracts.js` | Glimpse canonical entity shape |
| `Relation(id, source, target, type, weight, evidenceIds)` | same | Glimpse canonical edge shape |
| `Evidence(id, sourceRuleId, confidence, scope, targetId, affects, reason)` | same | Provenance-carrying evidence record |
| `ExtractedConcept(name, description, confidence, excerpt)` | `GRID-main/src/grid/knowledge/concept_extractor.py` | LLM/heuristic-extracted concept |
| `ExtractedRelation(from_concept, to_concept, relation_label, confidence)` | same | Extracted relationship |

### Safety and Governance Primitives

| Symbol | Location | Role |
|--------|----------|------|
| `ConsentType(EXPLICIT, IMPLICIT, NONE)` | `canopy/echoes/legal_safeguards.py` | Consent boundary enum |
| `ProtectionLevel(MINIMAL, STANDARD, MAXIMUM)` | same | Data protection tier |
| `CognitiveAccountingSystem.can_process(user_id, data_type) -> bool` | same | Consent gate |
| `CognitiveAccountingSystem._emit_provenance(...)` | same | Tamper-evident audit record |
| `ValueSystem.evaluate_response(response, context) -> dict[str, float]` | `canopy/echoes/app/values.py` | Graduated value scoring (respect, accuracy, helpfulness) |
| `ValueSystem.get_overall_score(scores) -> float` | same | Weighted composite 0.0-1.0 |

### Dimensional and Temporal Analysis

| Symbol | Location | Role |
|--------|----------|------|
| `buildEntities(records, profile, config)` | `glimpse-engine/analysis/entities.js` | Record -> entity with time/space/domain/catalyst dimensions |
| `buildBaseRelations(entities)` | `glimpse-engine/analysis/relations.js` | Entity pairs -> relations (influence, shared-space, temporal proximity) |
| `computeDimensionSimilarity(a, b, dimension)` | `glimpse-engine/analysis/similarity.js` | Fuzzy similarity: Levenshtein (space), token overlap (domain), temporal distance (time) |
| `detectTemporalClusters(timeValues, options)` | `glimpse-engine/analysis/temporal.js` | Gap-based 1D clustering with adaptive threshold |
| `bucketYearAdaptive(value, range)` | same | Range-aware temporal bucketing (5y / decade / quarter-century / century) |
| `computeTemporalDensity(timeValues)` | same | KDE-style density estimation over time dimension |

### Transformer Research References (Local)

| Asset | Location | Content |
|-------|----------|---------|
| Modern Transformer Guide | `grove/Vision/vision_llm_docs/modern-transformer-guide.md` | FlashAttention-2, RoPE, SLM token budgets |
| GRID RAG Engine | `GRID-main/src/tools/rag/rag_engine.py` | Production: embed -> store -> retrieve -> LLM |
| HuggingFace Embedding Provider | `GRID-main/src/tools/rag/embeddings/huggingface.py` | `SentenceTransformer` wrapper (production) |
| GRID Concept Extractor | `GRID-main/src/grid/knowledge/concept_extractor.py` | LLM/heuristic entity+relation extraction |
| Echoes Self-RAG Verifier | `canopy/echoes/api/self_rag.py` | Truth verification (simplified, no live retrieval) |
| Echoes RAG Orbit | `canopy/echoes/src/rag_orbit/` | Pseudo-embeddings (hashed, 384-d), FAISS-like retrieval (reference only) |

---

## Integration Architecture

The transformer research pattern that matters here is not "build attention layers from scratch"
but the **encode-index-retrieve-reason** pipeline that production systems use. The local
codebase already has the pieces; they are scattered.

```
                        ┌─────────────────────────────────────────────┐
                        │        Layer 1: Collective Priors           │
                        │  CrossReferenceSystem.domains               │
                        │  ValueSystem.values                         │
                        │  glimpse.master.yaml taxonomy + tone_cues   │
                        └──────────────────┬──────────────────────────┘
                                           │ config feeds runtime
                        ┌──────────────────▼──────────────────────────┐
                        │        Layer 2: Context Modulation          │
                        │  Mood state + PersonalityTraits             │
                        │  ConsentType + ProtectionLevel              │
                        │  Session history (loadHistory)              │
                        └──────────────────┬──────────────────────────┘
                                           │ state modulates decisions
                        ┌──────────────────▼──────────────────────────┐
                        │        Layer 3: Agentic Routing             │
                        │  IntentAwarenessEngine.detect_intent()      │
                        │  select_rule_pack(mood, consent)            │
                        │  governance_gates.check(op, user, scope)    │
                        └──────────────────┬──────────────────────────┘
                                           │ decisions route pipeline
                        ┌──────────────────▼──────────────────────────┐
                        │        Layer 4: Intelligence Hierarchy      │
                        │  S0: Ingest -> S1: Profile -> S2: Entity   │
                        │  S3: Relate -> S4: Score -> S5: Pattern    │
                        │  S6: Ground -> S7: Direct                  │
                        └─────────────────────────────────────────────┘
```

---

## Axis 1: Graph Compiler (`graph_compiler.py`)

Bridges Echoes `CrossReferenceSystem.analyze_context()` output into Glimpse `Entity` shape.

### Why This Matters

The cross-reference system already extracts domains, concepts, relationships, complexity, and
sentiment from text. But its output is an untyped dict that cannot feed into Glimpse's pipeline
(which expects `Entity` objects with `id`, `name`, `type`, `dimensions`, `domainKeywordHits`,
`tones`). The compiler is the type-safe bridge.

### Contract

```python
from dataclasses import dataclass


@dataclass
class CompiledEntity:
    """Mirrors Glimpse Entity contract (core/contracts.js).

    Emits BOTH camelCase and snake_case keys for the dual-key fields
    that Glimpse requires (domainKeywordHits AND domain_keyword_hits).
    """

    id: str
    name: str
    type: str  # "concept", "domain", "relation_node"
    dimensions: dict  # {time, space, domain, catalyst}
    metrics: dict
    domainKeywordHits: dict  # camelCase variant
    domain_keyword_hits: dict  # snake_case variant (same data)
    tones: dict  # camelCase
    tone_hits: dict  # snake_case (same data)
```

### Implementation Pattern

```python
import hashlib
from datetime import datetime, UTC

from core_modules.cross_reference_system import CrossReferenceSystem


def _stable_id(name: str) -> str:
    """Generate a stable entity ID from name, matching Glimpse's e-{slug} pattern."""
    slug = name.lower().strip().replace(" ", "-")[:40]
    return f"e-{slug}"


def compile_context_to_entities(
    context_output: dict,
    timestamp: str | None = None,
) -> list[dict]:
    """Convert CrossReferenceSystem.analyze_context() output to Glimpse Entity dicts.

    Args:
        context_output: Dict with keys: domains, key_concepts, relationships,
                        complexity, sentiment
        timestamp: Optional ISO timestamp for the time dimension

    Returns:
        List of dicts conforming to Glimpse Entity contract
    """
    entities = []
    ts = timestamp or datetime.now(UTC).isoformat()

    # Each identified domain becomes an entity
    for domain_name in context_output.get("domains", []):
        domain_hits = {domain_name: 1}
        entity = {
            "id": _stable_id(domain_name),
            "name": domain_name,
            "type": "domain",
            "dimensions": {
                "time": ts,
                "space": None,
                "domain": domain_name,
                "catalyst": None,
            },
            "metrics": {},
            "domainKeywordHits": domain_hits,
            "domain_keyword_hits": domain_hits,
            "tones": {},
            "tone_hits": {},
        }
        entities.append(entity)

    # Each key concept becomes an entity
    for concept in context_output.get("key_concepts", []):
        concept_hits = {}
        for domain_name in context_output.get("domains", []):
            concept_hits[domain_name] = 1 if domain_name in concept.lower() else 0

        entity = {
            "id": _stable_id(concept),
            "name": concept,
            "type": "concept",
            "dimensions": {
                "time": ts,
                "space": None,
                "domain": context_output.get("domains", [None])[0],
                "catalyst": None,
            },
            "metrics": {
                "complexity": {"high": 1.0, "medium": 0.5, "low": 0.2}.get(
                    context_output.get("complexity", "low"), 0.2
                ),
            },
            "domainKeywordHits": concept_hits,
            "domain_keyword_hits": concept_hits,
            "tones": {"sentiment": context_output.get("sentiment", "neutral")},
            "tone_hits": {"sentiment": context_output.get("sentiment", "neutral")},
        }
        entities.append(entity)

    return entities
```

### Acceptance Test Shape

```python
def test_compile_produces_valid_entities():
    context = {
        "domains": ["technology", "science"],
        "key_concepts": ["machine learning", "neural networks", "optimization"],
        "relationships": [{"type": "domain_connection", "domains": ["technology", "science"]}],
        "complexity": "high",
        "sentiment": "analytical",
    }

    entities = compile_context_to_entities(context)

    assert len(entities) == 5  # 2 domains + 3 concepts
    for e in entities:
        assert "id" in e and e["id"].startswith("e-")
        assert "name" in e and isinstance(e["name"], str)
        assert "type" in e and e["type"] in ("domain", "concept")
        assert "dimensions" in e and "time" in e["dimensions"]
        assert "domainKeywordHits" in e  # camelCase
        assert "domain_keyword_hits" in e  # snake_case
        assert e["domainKeywordHits"] == e["domain_keyword_hits"]
```

---

## Axis 2: Agentic Routing Kernel (`select_rule_pack`)

Maps current mood + consent state to a rule-pack boundary that controls which
exploratory paths are accessible.

### Why This Matters

All creativity mechanisms (simulations, analogies, humor, mood adaptation) are currently
**latent**: reachable from the CLI but with no governance boundary. The rule-pack selection
creates a typed gate between context state and pipeline behavior.

### Truth Table

```
┌─────────────┬──────────────────────┬──────────────────┐
│ ConsentType │ CREATIVE / CURIOUS   │ All other moods  │
├─────────────┼──────────────────────┼──────────────────┤
│ EXPLICIT    │ exploratory          │ base             │
│ IMPLICIT    │ base                 │ base             │
│ NONE        │ restricted           │ restricted       │
└─────────────┴──────────────────────┴──────────────────┘
```

### Implementation Pattern

```python
# In core_modules/personality_engine.py

from legal_safeguards import ConsentType


EXPLORATORY_MOODS = {Mood.CREATIVE, Mood.CURIOUS}


def select_rule_pack(mood: Mood, consent: ConsentType) -> str:
    """Determine which rule-pack governs the current session.

    Fail-closed: unknown consent defaults to restricted.
    """
    if consent == ConsentType.NONE:
        return "restricted"
    if consent == ConsentType.EXPLICIT and mood in EXPLORATORY_MOODS:
        return "exploratory"
    return "base"
```

### Acceptance Test Shape

```python
import pytest
from core_modules.personality_engine import Mood, select_rule_pack
from legal_safeguards import ConsentType


@pytest.mark.parametrize(
    "mood,consent,expected",
    [
        (Mood.CREATIVE, ConsentType.EXPLICIT, "exploratory"),
        (Mood.CURIOUS, ConsentType.EXPLICIT, "exploratory"),
        (Mood.FOCUSED, ConsentType.EXPLICIT, "base"),
        (Mood.SUPPORTIVE, ConsentType.IMPLICIT, "base"),
        (Mood.CREATIVE, ConsentType.IMPLICIT, "base"),
        (Mood.CREATIVE, ConsentType.NONE, "restricted"),
        (Mood.FOCUSED, ConsentType.NONE, "restricted"),
    ],
)
def test_select_rule_pack(mood, consent, expected):
    assert select_rule_pack(mood, consent) == expected
```

---

## Axis 3: Governance Gates (`governance_gates.py`)

Composes consent check + value threshold into a single `GateVerdict` with provenance.

### Why This Matters

`can_process()` exists in `legal_safeguards.py` but is never called from production paths.
`ValueSystem.evaluate_response()` exists but `_improve_response()` is never invoked.
The governance gate wires both into a single callable that emits audit-grade provenance.

### Contract

```python
from dataclasses import dataclass, field
from datetime import datetime, UTC
from uuid import uuid4


@dataclass
class GateVerdict:
    """Result of a governance gate evaluation."""

    allowed: bool
    reason: str
    provenance_id: str = field(default_factory=lambda: str(uuid4()))
    confidence: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
```

### Implementation Pattern

```python
from app.values import get_value_system
from legal_safeguards import CognitiveAccountingSystem, ConsentType, ProtectionLevel


def check(
    accounting: CognitiveAccountingSystem,
    operation_type: str,
    user_id: str,
    scope: str,
    value_threshold: float = 0.5,
) -> GateVerdict:
    """Evaluate whether an operation is permitted.

    Composes:
    1. Consent gate (CognitiveAccountingSystem.can_process)
    2. Value threshold (ValueSystem.evaluate_response >= threshold)

    Emits provenance record regardless of outcome.
    """
    # Map scope to protection level
    protection_map = {
        "personal": ProtectionLevel.MAXIMUM,
        "creative": ProtectionLevel.STANDARD,
        "general": ProtectionLevel.MINIMAL,
    }
    data_type = scope
    protection = protection_map.get(scope, ProtectionLevel.STANDARD)
    accounting.set_protection(data_type, protection)

    consent_allowed = accounting.can_process(user_id, data_type)

    if not consent_allowed:
        return GateVerdict(
            allowed=False,
            reason=f"Consent gate denied: user={user_id}, scope={scope}",
            confidence=0.95,
        )

    # Value system check
    vs = get_value_system()
    scores = vs.evaluate_response(
        f"Operation: {operation_type} for scope: {scope}",
        context={"user_id": user_id, "operation": operation_type},
    )
    overall = vs.get_overall_score(scores)

    if overall < value_threshold:
        return GateVerdict(
            allowed=False,
            reason=f"Value threshold not met: {overall:.2f} < {value_threshold}",
            confidence=overall,
        )

    return GateVerdict(
        allowed=True,
        reason=f"Authorized: consent=pass, values={overall:.2f}",
        confidence=overall,
    )
```

### Acceptance Test Shape

```python
from legal_safeguards import CognitiveAccountingSystem, ConsentType


def test_none_consent_blocks():
    cas = CognitiveAccountingSystem()
    # Do NOT set consent (defaults to NONE)
    verdict = check(cas, "simulation", "user-1", "personal")
    assert verdict.allowed is False
    assert "Consent gate denied" in verdict.reason


def test_explicit_consent_allows():
    cas = CognitiveAccountingSystem()
    cas.set_consent("user-1", ConsentType.EXPLICIT)
    verdict = check(cas, "chat", "user-1", "general")
    assert verdict.allowed is True


def test_provenance_chain_grows():
    cas = CognitiveAccountingSystem()
    cas.set_consent("user-1", ConsentType.EXPLICIT)
    initial_len = len(cas.provenance_chain)
    check(cas, "chat", "user-1", "general")
    assert len(cas.provenance_chain) > initial_len
```

---

## Axis 4: Terminal Entry Point (`atlas_repl.py`)

Interactive stdin loop that threads all axes together.

### Why This Matters

The assistant CLI (`assistant_v2_core.py`) is a 4500-line monolith. The atlas REPL is a focused
alternative: thin, composable, and governance-aware from the first line.

### Implementation Pattern

```python
#!/usr/bin/env python3
"""Atlas REPL: knowledge-graph exploration from the terminal.

Usage:
    echo "quantum computing" | python scripts/atlas_repl.py
    python scripts/atlas_repl.py --mood CREATIVE --preset exploratory
"""

import argparse
import json
import subprocess
import sys

from core_modules.cross_reference_system import CrossReferenceSystem
from core_modules.personality_engine import Mood, PersonalityEngine, select_rule_pack
from core_modules.governance_gates import check, GateVerdict
from core_modules.graph_compiler import compile_context_to_entities
from legal_safeguards import CognitiveAccountingSystem, ConsentType


def try_glimpse_pipeline(entities: list[dict]) -> dict | None:
    """Attempt to run entities through Glimpse engine via subprocess.

    Returns pipeline result dict or None if Glimpse is unavailable.
    """
    script = f"""
    import('{"/home/caraxes/CascadeProjects/Applications/glimpse-engine/core/engine.js"}')
      .then(eng => {{
        const result = eng.runContextPipeline({json.dumps(entities)}, 'json', {{
          inference: {{ multi_pass: false }},
          taxonomy: {{ domains: [] }},
          defaults: {{ active_preset: 'analyst' }},
          function_registry: {{
            field_exists: {{ scope: ['dataset','entity'], args: {{ path: 'field_selector' }} }},
            taxonomy_score: {{ scope: ['entity'], args: {{ path: 'field_selector', domain: 'lens_id', min_score: 'numeric_threshold' }} }},
            dimension_count: {{ scope: ['dataset'], args: {{ dimension: 'dimension_name', min_count: 'numeric_threshold' }} }},
            record_range: {{ scope: ['dataset'], args: {{ min: 'numeric_threshold', max: 'numeric_threshold' }} }}
          }},
          rules: []
        }});
        if (result) {{
          console.log(JSON.stringify({{
            primaryLens: result.primaryLens?.label || null,
            relations: (result.relations || []).slice(0, 3).map(r => ({{
              source: result.entities?.find(e => e.id === r.source)?.name || r.source,
              target: result.entities?.find(e => e.id === r.target)?.name || r.target,
              type: r.type
            }})),
            entityCount: result.entities?.length || 0,
            complexity: result.complexity?.level || 'unknown'
          }}));
        }} else {{
          console.log(JSON.stringify({{ error: 'null result' }}));
        }}
      }})
      .catch(e => console.log(JSON.stringify({{ error: e.message }})));
    """
    try:
        proc = subprocess.run(
            ["node", "-e", script],
            capture_output=True, text=True, timeout=5,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return json.loads(proc.stdout.strip())
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return None


def format_output(
    context: dict,
    entities: list[dict],
    glimpse_result: dict | None,
    rule_pack: str,
    verdict: GateVerdict,
) -> str:
    """Format structured terminal output."""
    lines = []

    if glimpse_result and "error" not in glimpse_result:
        lines.append(f"  lens: {glimpse_result.get('primaryLens', '(none)')}")
        for r in glimpse_result.get("relations", []):
            lines.append(f"  edge: {r['source']} -> {r['target']} ({r['type']})")
        lines.append(f"  complexity: {glimpse_result.get('complexity', '?')}")
    else:
        # Echoes-only fallback
        lines.append(f"  domains: {', '.join(context.get('domains', []))}")
        lines.append(f"  concepts: {', '.join(context.get('key_concepts', []))}")
        lines.append(f"  complexity: {context.get('complexity', '?')}")

    lines.append(f"  rule-pack: {rule_pack}")
    lines.append(f"  gate: {'pass' if verdict.allowed else 'BLOCKED'} ({verdict.reason})")
    lines.append(f"  entities: {len(entities)}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Atlas knowledge-graph REPL")
    parser.add_argument("--mood", default="FOCUSED", choices=[m.name for m in Mood])
    parser.add_argument("--preset", default="base")
    parser.add_argument("--user-id", default="atlas-user")
    args = parser.parse_args()

    mood = Mood[args.mood]
    cross_ref = CrossReferenceSystem()
    personality = PersonalityEngine()
    accounting = CognitiveAccountingSystem()
    accounting.set_consent(args.user_id, ConsentType.EXPLICIT)

    for line in sys.stdin:
        text = line.strip()
        if not text:
            continue

        # Layer 2: context modulation
        personality.update_from_interaction(text)
        current_mood = personality.current_mood

        # Layer 3: agentic routing
        rule_pack = select_rule_pack(current_mood, accounting.get_consent(args.user_id))
        verdict = check(accounting, "atlas_query", args.user_id, "general")

        if not verdict.allowed:
            print(f"  BLOCKED: {verdict.reason}")
            continue

        # Layer 1 + Layer 4: compile and run
        context = cross_ref.analyze_context(text)
        entities = compile_context_to_entities(context)
        glimpse_result = try_glimpse_pipeline(entities)

        print(format_output(context, entities, glimpse_result, rule_pack, verdict))


if __name__ == "__main__":
    main()
```

---

## Dimensional and Temporal Awareness

The Glimpse engine already implements sophisticated temporal analysis. Here is how the
atlas layer should consume it.

### Temporal Cluster Detection

Glimpse's `detectTemporalClusters` uses adaptive gap-based splitting:

```javascript
// From glimpse-engine/analysis/temporal.js
// Input: array of year values
// Output: clusters with center, spread, members, label

const clusters = detectTemporalClusters([1831, 1859, 1865, 1888, 1900, 1905, 1936, 1948]);
// -> [{center: 1860, spread: 14, members: [1831,1859,1865,1888], label: "1831-1888"},
//     {center: 1922, spread: 20, members: [1900,1905,1936,1948], label: "1900-1948"}]
```

### Dimension Similarity

The similarity module supports three dimension types with different strategies:

```javascript
// Space: Levenshtein + alias normalization
computeDimensionSimilarity("New York", "NYC", "space");
// -> {score: 0.85, method: "alias", matched: true}

// Time: temporal distance (closer = higher score)
computeDimensionSimilarity(1905, 1913, "time");
// -> {score: 0.84, method: "temporal-distance", matched: true}

// Domain: token overlap (Jaccard coefficient)
computeDimensionSimilarity("machine learning", "deep learning", "domain");
// -> {score: 0.5, method: "token-overlap", matched: true}
```

### Integration with Atlas Entities

When the graph compiler produces entities with time/space/domain dimensions, the Glimpse
pipeline automatically detects clusters and relations through `buildBaseRelations`:

1. **Temporal proximity**: entities within adaptive bucket range get `shared-time` relations
2. **Spatial similarity**: fuzzy string matching on location dimension creates `shared-space` relations
3. **Influence chains**: `influenced_by` / `catalyst` columns produce explicit `influenced` edges
4. **Domain overlap**: shared taxonomy keywords create cross-domain bridge relations

---

## Safety Integration Points

### Where Safety Gates Fire in the Pipeline

```
stdin text
    │
    ▼
┌──────────────────────────────┐
│ governance_gates.check()     │  <-- consent + value threshold
│ If BLOCKED: print reason,   │
│ skip pipeline, continue loop │
└──────────────┬───────────────┘
               │ allowed=true
               ▼
┌──────────────────────────────┐
│ select_rule_pack(mood,       │  <-- determines what paths are available
│   consent) -> str            │
│                              │
│ "restricted" = no simulation,│
│   no analogy, no humor       │
│ "base" = standard pipeline   │
│ "exploratory" = full creative│
│   paths + multi-pass         │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Pipeline execution           │
│ (compile -> entities ->      │
│  relations -> lenses)        │
│                              │
│ Every Evidence record carries│
│ sourceRuleId + confidence    │  <-- provenance at stratum level
└──────────────────────────────┘
```

### Provenance Chain Structure

Every governance gate call and consent change produces a provenance record:

```python
# Example provenance record from _emit_provenance
{
    "decision_type": "gate_verdict",
    "action_taken": "data_processing_authorization",
    "actor_id": "atlas-user",
    "reasoning": "Processing authorized: consent=explicit, protection=minimal",
    "authority": "system_policy",
    "verdict": "pass",
    "gate_id": "consent_gate:general",
    "timestamp": "2026-04-04T15:30:00Z",
    "hash": "a1b2c3..."  # HMAC chain for tamper evidence
}
```

### Non-Escalation Invariant

Downstream strata cannot claim higher confidence than their input evidence:

```python
def enforce_non_escalation(upstream_confidence: float, downstream_claim: float) -> float:
    """Clamp downstream confidence to upstream maximum.

    This is the Layer 4 contract: no stratum may inflate confidence
    beyond what the evidence supports.
    """
    return min(upstream_confidence, downstream_claim)
```

---

## Cross-Stack Symbol Reference

For quick lookup when implementing across the Echoes/Glimpse boundary.

### Echoes -> Glimpse Field Mapping

| Echoes field | Glimpse Entity field | Notes |
|-------------|---------------------|-------|
| `domain` (from analyze_context) | `dimensions.domain` | Direct map |
| `sentiment` (from analyze_context) | `tones.sentiment` | Must also emit as `tone_hits.sentiment` |
| `complexity` (high/medium/low) | `metrics.complexity` | Convert to float: high=1.0, medium=0.5, low=0.2 |
| `key_concepts` list | One entity per concept | Each concept becomes a separate Entity |
| `relationships` list | Fed to `buildBaseRelations` via catalyst/influenced_by columns | Requires mapping to Glimpse's `influenced_by` pattern |

### Glimpse -> Echoes Result Mapping

| Glimpse result field | Echoes usage | Notes |
|---------------------|-------------|-------|
| `primaryLens.label` | Display as "lens:" in REPL output | String |
| `relations[].source/target` | Display as "edge: A -> B" | Resolve entity IDs to names |
| `complexity.level` | Display as "complexity:" | String (simple/moderate/complex) |
| `confidenceReport.overallScore` | Feed to non-escalation check | Float 0-1 |

---

## Verification Checklist

Before marking any axis complete:

- [ ] All required Entity fields present (including dual-key variants)
- [ ] Governance gate fires before pipeline execution
- [ ] Provenance chain length increases monotonically per gate call
- [ ] Rule-pack correctly reflects mood x consent truth table
- [ ] Non-escalation invariant holds across all strata
- [ ] Glimpse-unavailable fallback produces valid (reduced) output
- [ ] No circular imports between personality_engine and legal_safeguards
- [ ] All test assertions use concrete expected values, not vague "is not None"
