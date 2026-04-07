# Echoes ecosystem release — tracking artifact

```yaml
track: "Echoes seven-axis verification + critical-path breadth (G-360 depth 0); category PR scheduling"
sort: [severity_rank, pr_category, target, id]
flags:
  high_only: false
  backlog_linked: false
  open_only: true
  recursive_children: true
  integration_debate_focus: false
fast_lap:
  focus: backlog_analysis
  last_run_utc: "2026-04-06"
```

**Severity rank** (for future findings rows): HIGH=0, MED=1, LOW=2. **PR category order:** security → feat → fix → refactor → test → chore.

## Gates (Phase A / fast lap)

| Gate        | Command | Last validated |
|-------------|---------|----------------|
| Atlas integration | `uv run pytest tests/test_atlas_integration.py -q` | **36 passed** |
| Drift | `uv run python scripts/atlas_drift_check.py` | **exit 0** (embeddedness stable) |
| Full suite | `uv run pytest tests/ -q` | **339 passed**, 90 skipped |
| Ruff (scoped) | `uv run ruff check integrations tests/test_impact_analytics_integration.py` | **clean** (full `uv run ruff check .` not re-run here) |

Note: Full-repo `uv run ruff check .` may still report historical issues outside touched paths; CI should converge per PR. Prefer **`uv run`** for all Python entrypoints in this repo (see [CLAUDE.md](../CLAUDE.md)).

## Inventory — linked to [data/implementation_backlog.json](../data/implementation_backlog.json)

Sorted by **axis**, then **target_file**, then **id** (stable signature for backlog rows).

| id | axis | severity_rank | target | one_liner | acceptance | pr_category | depends_on | next_up |
|----|------|---------------|--------|-----------|------------|-------------|------------|---------|
| BL-1 | 1 | 2 | core_modules/graph_compiler.py | Compile CrossRef context → Glimpse Entity dicts | pytest graph compiler suite | test(coverage) | — | false |
| BL-2 | 2 | 2 | core_modules/personality_engine.py | Rule-pack from Mood × Consent | pytest test_atlas_routing | test(coverage) | — | false |
| BL-3 | 3 | 2 | core_modules/governance_gates.py | Governance GateVerdict composition | pytest test_atlas_governance | test(coverage) | — | false |
| BL-4 | 4 | 2 | scripts/atlas_repl.py | CLI Atlas + optional Glimpse | pytest test_atlas_repl | test(coverage) | — | false |
| BL-5 | 5 | 2 | tests/test_atlas_integration.py + scripts/atlas_drift_check.py | Integration + drift chain | integration + drift script exit 0 | test(coverage) | — | false |
| BL-0a | 0 | 2 | assistant_v2_core.py | can_process on chat path | assistant / consent tests | test(coverage) | — | false |
| BL-0b | 0 | 2 | pyproject.toml | core_modules under ruff | ruff check core_modules | chore(tooling) | — | false |
| BL-0c | 0 | 2 | app/agents/agent.py | sanitize_prompt before API | agent / safety tests | test(coverage) | — | false |

All backlog JSON rows carry `status: complete`; **next_up** is false while verification gates stay green and no new HIGH finding row exists.

## G-360 depth 0 — critical-path breadth (integration surfaces)

| id | target | one_liner | debate_topic (if integration_debate_focus) |
|----|--------|-----------|---------------------------------------------|
| CP-1 | assistant_v2_core.py | Main CLI/session orchestration; optional imports | — |
| CP-2 | app/agents/agent.py | OpenAI path + sanitize_prompt + logging | Single sanitization owner vs API layer |
| CP-3 | api/main.py | WS /metrics / pattern_detection / structlog | — |
| CP-4 | app/knowledge/ | Context/memory (app layer) vs core CrossRef | — |
| CP-5 | scripts/atlas_repl.py | CrossRef → compile → governance → Node bridge | Python logging vs Node JSON stdout contract |

Deepening to depth 1–5 only when a **debate_topic** stays unresolved (Gruff neck height).

## Phase B queue (execute when findings rehydrated)

1. **feat(integration)** — Atlas/Glimpse degradation paths (unchanged backlog I/O).
2. **feat(api|assistant)** — User-visible behavior + tests.
3. **fix(security|governance)** — Consent / provenance regressions + pytest.
4. **refactor(observability)** — `structlog` on chat/request paths; reduce bare `print` in assistant core.
5. **test(coverage)** — Expand coverage for new branches; keep `integrations` exercised.
6. **chore(tooling)** — Ruff/mypy/CI in small PRs.

## Completed in this execution (mechanical)

- **`integrations` package**: offline-safe IMPACT/Turbo stubs; fixed test `sys.path` so imports resolve from repo root.
- **Bridge logging doc**: [atlas_repl_bridge_logging.md](atlas_repl_bridge_logging.md).

Suggested commit messages (category-scoped):

- `feat(integrations): add offline impact analytics stubs for tests`
- `fix(tests): correct integrations import path in impact analytics tests`
- `docs: add release tracking artifact and atlas REPL bridge logging`
