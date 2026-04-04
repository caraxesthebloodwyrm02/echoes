# Atlas

Hierarchical knowledge-graph workflow for the Echoes platform.
Bridges concept analysis, governance gates, and graph compilation into a single
terminal-native pipeline with optional Glimpse engine integration.

## What This Is

Atlas is a four-layer architecture grounded in a simple idea: raw text enters,
typed graph entities leave, and every decision along the way is governed and traced.

```
text in -> context analysis -> governance gate -> graph compile -> pipeline -> structured out
```

The four layers:

1. **Collective** -- shared taxonomy, values, tone cues (config-level, read-only per session)
2. **Context** -- mood state, consent type, session history (mutable, provenance-tracked)
3. **Agentic** -- intent detection, rule-pack selection, governance verdicts (decision routing)
4. **Hierarchy** -- records -> entities -> relations -> lenses -> patterns -> insights -> directives

Full schema: `docs/atlas_schema.md`

## Quick Start

```bash
# From canopy/echoes on branch atlas/scaffold-offline

# Run the REPL (stdin, one line at a time)
echo "How do neural networks relate to biological systems?" | \
  JWT_SECRET=dev-secret python scripts/atlas_repl.py --mood CREATIVE

# Run verification suite (36 tests)
JWT_SECRET=dev-secret python -m pytest tests/test_atlas_integration.py -v \
  --override-ini="addopts="

# Run drift monitor
python scripts/atlas_drift_check.py
```

## Modules

| File | Role |
|------|------|
| `core_modules/graph_compiler.py` | Echoes context -> Glimpse Entity shape (dual-key emission) |
| `core_modules/governance_gates.py` | Consent + value threshold -> `GateVerdict` with provenance |
| `core_modules/personality_engine.py` | `select_rule_pack(mood, consent)` -- 21-case truth table |
| `app/agents/agent.py` | `sanitize_prompt()` -- 8 injection-pattern blocklist |
| `scripts/atlas_repl.py` | Terminal REPL with Glimpse subprocess bridge + fallback |
| `scripts/atlas_drift_check.py` | Embeddedness regression monitor |
| `tests/test_atlas_integration.py` | 36-test verification suite across all axes |

## Rule-Pack Selection

| Consent | CREATIVE / CURIOUS | All other moods |
|---------|-------------------|-----------------|
| EXPLICIT | `exploratory` | `base` |
| IMPLICIT | `base` | `base` |
| NONE | `restricted` | `restricted` |

`restricted` disables simulation, analogy, and humor paths.
`exploratory` enables multi-pass inference and creative graph expansion.

## Governance Gate

Every pipeline invocation passes through `governance_gates.check()` before
any entities are compiled or returned. The gate composes:

1. `CognitiveAccountingSystem.can_process()` -- consent boundary
2. `ValueSystem.evaluate_response()` -- respect/accuracy/helpfulness threshold (>= 0.5)

Returns a `GateVerdict` dataclass: `allowed`, `reason`, `provenance_id`, `confidence`.
Provenance chain grows monotonically per call (HMAC-signed, requires `JWT_SECRET`).

## Graph Compiler Output Shape

Each compiled entity conforms to Glimpse's `Entity` contract:

```
{
  id:                  "e-{slug}",
  name:                str,
  type:                "domain" | "concept" | "relation_node",
  dimensions:          {time, space, domain, catalyst},
  metrics:             {complexity: float},
  domainKeywordHits:   dict,
  domain_keyword_hits: dict,   # same data, dual-key for Glimpse compat
  tones:               dict,
  tone_hits:           dict    # same data, dual-key
}
```

## Glimpse Bridge

The REPL calls `node -e` with a dynamic import of
`CascadeProjects/Applications/glimpse-engine/core/engine.js`.
If node or the engine is unavailable, output degrades to Echoes-only
cross-reference results (domains, concepts, complexity). Timeout: 5 seconds.

## Theme

`docs/atlas-theme.css` defines the visual language:

- **Background**: deep umber `#1c1714`
- **Skin tones**: `#f5ebe0` (lightest text) through `#8b6f54` (muted labels)
- **Brown contrast**: `#6b5340` (borders) through `#261c14` (heavy anchoring)
- **Accent**: `#c2956b` warm gold, damped (links, active nodes, primary actions)
- **Semantic**: sage green (pass), warm amber (warn), terracotta (deny), dusty steel (info)

Includes graph node and edge tokens for SVG rendering.

## Files Not Tracked

Runtime artifacts excluded via `.gitignore`:

- `data/build_phase_ledger.json` -- regenerated from GitHub API
- `data/gap_taxonomy_matrix.json` -- regenerated from code inspection
- `data/implementation_backlog.json` -- regenerated from synthesis
- `data/atlas_sessions/` -- ephemeral REPL state
- `docs/atlas-theme-tokens.json` -- derived from CSS source

## Branch

`atlas/scaffold-offline` -- works fully offline, no remote push required.
Diverges from `master` by one commit.

## Verification

```bash
# All 36 tests
JWT_SECRET=dev-secret python -m pytest tests/test_atlas_integration.py -v \
  --override-ini="addopts="

# Drift monitor (embeddedness regression check)
python scripts/atlas_drift_check.py

# REPL smoke test
echo "quantum computing" | JWT_SECRET=dev-secret python scripts/atlas_repl.py
```

## Dependencies

No new packages. Uses only what Echoes already ships:
`CrossReferenceSystem`, `PersonalityEngine`, `CognitiveAccountingSystem`,
`ValueSystem`, `IntentAwarenessEngine` -- all from `core_modules/` and `app/`.

Glimpse bridge is optional (subprocess to node).
