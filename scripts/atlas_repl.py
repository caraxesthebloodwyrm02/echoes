#!/usr/bin/env python3
"""Atlas REPL: knowledge-graph exploration from the terminal.

Threads all Atlas axes together:
  stdin -> context analysis -> graph compile -> governance gate ->
  rule-pack select -> (optional) Glimpse pipeline -> structured output

Usage:
    echo "quantum computing and neural networks" | uv run python scripts/atlas_repl.py
    uv run python scripts/atlas_repl.py --mood CREATIVE --user-id researcher-1
    uv run python scripts/atlas_repl.py < journal.txt
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_modules.cross_reference_system import CrossReferenceSystem
from core_modules.personality_engine import Mood, PersonalityEngine, select_rule_pack
from core_modules.graph_compiler import (
    compile_context_to_entities,
    validate_entities,
    detect_partition_conflicts,
)
from core_modules.governance_gates import check as governance_check, GateVerdict
from core_modules.partition_conflict_pipeline import (
    run_conflict_pipeline,
    apply_resolution_states,
    append_partition_registry,
)

try:
    from legal_safeguards import CognitiveAccountingSystem, ConsentType
    LEGAL_AVAILABLE = True
except ImportError:
    LEGAL_AVAILABLE = False
    CognitiveAccountingSystem = None
    ConsentType = None

GLIMPSE_ENGINE_PATH = "/home/caraxes/CascadeProjects/Applications/glimpse-engine"


def try_glimpse_pipeline(entities: list[dict]) -> dict | None:
    """Run entities through Glimpse engine via node subprocess.

    Returns parsed result dict or None if Glimpse is unavailable.
    Latency budget: 5s timeout.
    """
    records_json = json.dumps(entities)
    script = f"""
    import('{GLIMPSE_ENGINE_PATH}/core/engine.js')
      .then(eng => {{
        const result = eng.runContextPipeline({records_json}, 'json', {{
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
              source: (result.entities || []).find(e => e.id === r.source)?.name || r.source,
              target: (result.entities || []).find(e => e.id === r.target)?.name || r.target,
              type: r.type
            }})),
            entityCount: (result.entities || []).length,
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
            capture_output=True,
            text=True,
            timeout=5,
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
    conflict_summaries: list[dict] | None = None,
) -> str:
    lines = []

    if glimpse_result and "error" not in glimpse_result:
        lines.append(f"  lens: {glimpse_result.get('primaryLens', '(none)')}")
        for r in glimpse_result.get("relations", []):
            lines.append(f"  edge: {r['source']} -> {r['target']} ({r['type']})")
        lines.append(f"  complexity: {glimpse_result.get('complexity', '?')}")
    else:
        lines.append(f"  domains: {', '.join(context.get('domains', []))}")
        concepts = context.get("key_concepts", [])
        lines.append(f"  concepts: {', '.join(concepts[:5])}")
        lines.append(f"  complexity: {context.get('complexity', '?')}")

    lines.append(f"  rule-pack: {rule_pack}")
    lines.append(f"  gate: {'pass' if verdict.allowed else 'BLOCKED'} ({verdict.reason})")
    lines.append(f"  entities: {len(entities)}")
    summaries = conflict_summaries or []
    if summaries:
        blocked = sum(len(item.get("blocked_entity_ids", [])) for item in summaries)
        lines.append(f"  conflicts: {len(summaries)} resolved, blocked={blocked}")
    else:
        lines.append("  conflicts: 0")
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

    accounting = None
    consent = None
    if LEGAL_AVAILABLE:
        accounting = CognitiveAccountingSystem()
        accounting.set_consent(args.user_id, ConsentType.EXPLICIT)
        consent = ConsentType.EXPLICIT
    else:
        from types import SimpleNamespace
        consent = SimpleNamespace(value="explicit")

    for line in sys.stdin:
        text = line.strip()
        if not text:
            continue

        personality.update_from_interaction(text)
        current_mood = personality.current_mood

        rule_pack = select_rule_pack(current_mood, consent)
        verdict = governance_check(accounting, "atlas_query", args.user_id, "general")

        if not verdict.allowed:
            print(f"  BLOCKED: {verdict.reason}")
            continue

        context = cross_ref.analyze_context(text)
        entities = compile_context_to_entities(context)

        validation_errors = validate_entities(entities)
        if validation_errors:
            for err in validation_errors:
                print(f"  WARN: {err}", file=sys.stderr)

        conflicts = detect_partition_conflicts(entities)
        conflict_summaries = run_conflict_pipeline(conflicts) if conflicts else []
        if conflict_summaries:
            apply_resolution_states(entities, conflict_summaries)

        # Keep an append-only registry of entity partition assignments.
        append_partition_registry(entities)

        active_entities = [e for e in entities if e.get("conflict_state") != "blocked"]
        glimpse_result = try_glimpse_pipeline(active_entities)
        print(
            format_output(
                context,
                active_entities,
                glimpse_result,
                rule_pack,
                verdict,
                conflict_summaries,
            )
        )


if __name__ == "__main__":
    main()
