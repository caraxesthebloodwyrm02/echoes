# EchoesAssistantV2 → EchoesAgentsV1 symbol map (audit)

Graduation-oriented inventory of the main assistant type, its neighbors, and suggested v1 boundaries. **EchoesAssistantV2 is a class** (not a `@dataclass`); neighboring helpers use dataclasses where noted.

**Primary definition:** [`assistant_v2_core.py`](../../assistant_v2_core.py) — `EchoesAssistantV2` (starts ~line 455).

This document maps the **assistant core type** and its **direct neighbors**. It does **not** exhaust every script under `misc/` or every Docker layout; those are listed under **Omissions**.

## Entry points (where execution starts)

| Surface | How it is launched | Typical role |
|--------|---------------------|--------------|
| **Interactive CLI assistant** | `uv run python assistant_v2_core.py` → `interactive_mode()` / `__main__` | Primary human-facing assistant; constructs `EchoesAssistantV2`. |
| **HTTP + WebSocket API** | `uv run uvicorn api.main:app` or `python -m api.main` (uses [`api/config.py`](../../api/config.py) host/port) | REST patterns/truth/simulation feedback + **`/ws/stream`**; does **not** instantiate `EchoesAssistantV2` per request (pattern/truth handlers call modules directly). |
| **Operational security CLI** | `uv run python -m tools.security` ([`tools/security/__main__.py`](../../tools/security/__main__.py)) | Heuristic secret/PII redaction and detection on stdin or files — shared **policy** with optional [`redact_telemetry_processor`](../../api/logging_structured.py). |
| **Atlas / pipeline scripts** | e.g. [`scripts/atlas_drift_check.py`](../../scripts/atlas_drift_check.py), [`scripts/atlas_repl.py`](../../scripts/atlas_repl.py) | Offline drift / REPL checks; integration **scope** overlaps Glimpse + JWT env (`JWT_SECRET`) but not the full assistant graph. |
| **Demos & tests** | [`demos/`](../../demos/), [`tests/`](../../tests/) | Import `EchoesAssistantV2` or API helpers for scenarios — treat as **consumers**, not production entrypoints. |
| **Containers** | [`docker-compose.yml`](../../docker-compose.yml), [`docker/docker-compose.prod.yml`](../../docker/docker-compose.prod.yml) | Orchestration only; runtime command still **`uvicorn api.main:app`** (or image CMD). |

## Integration scopes (who talks to whom)

```text
┌─────────────────────┐     ┌──────────────────────────────┐
│  EchoesAssistantV2  │     │  FastAPI app (api.main)       │
│  (CLI / demos)      │     │  REST + WS /metrics /health   │
└─────────┬───────────┘     └───────────────┬──────────────┘
          │                                  │
          │  shared OpenAI client pattern    │  detect_patterns, verify_truth,
          │  optional tools/registry         │  parallel_simulation feedback
          │                                  │
          ▼                                  ▼
┌─────────────────────────────────────────────────────────────┐
│ Global singletons & engines (intent, thought_tracker,        │
│ parallel_simulation, glimpse, legal/accounting when enabled) │
└─────────────────────────────────────────────────────────────┘
```

| Boundary | In scope for EchoesAgentsV1 extraction | Notes |
|----------|------------------------------------------|--------|
| **Assistant vs HTTP API** | Different binaries: assistant is sync OpenAI + mixins; API is async FastAPI and **does not** route all paths through `EchoesAssistantV2`. | Shared **modules** (`parallel_simulation`, pattern/truth) are the collaboration surface. |
| **Assistant vs `app.agents`** | **`Agent` / `ConversationHistory`** ([`app/agents/models.py`](../../app/agents/models.py)) remain a **parallel** agent stack (`chat.completions`). | **`AgentWorkflow`** holds an assistant reference — explicit **integration seam**. |
| **Auth middleware vs WebSocket** | HTTP routes use [`AuthenticationMiddleware`](../../api/middleware.py) when `API_KEY_REQUIRED`; **`BaseHTTPMiddleware` does not run for WebSocket upgrades** in Starlette — WS **`/ws/stream`** must be treated as a **separate auth scope** for production (handshake token or route guard). |
| **External collaboration** | OpenAI APIs, optional Redis, optional Glimpse subprocess tooling (`scripts/atlas_repl.py`). | Anything labeled **MCP / editor tooling** is **environment** outside this repo’s Python graph — omit implementation detail here. |

## Shared ground (data & configuration)

| Asset | Location / mechanism | Used by |
|-------|----------------------|---------|
| **Environment & API config** | [`api/config.py`](../../api/config.py), `OPENAI_API_KEY`, `ALLOWED_API_KEYS`, `JWT_SECRET` (provenance) | API + assistant + legal signing |
| **Session / memory files** | `data/memory` (via `MemoryStore` in `assistant_v2_core`) | CLI assistant |
| **Simulation outcomes** | `parallel_simulation` + REST **`/api/simulation/outcome-feedback`** | API + core modules |
| **Motivation tokens** | [`core_modules/motifs.py`](../../core_modules/motifs.py) (`Abrasive`, catalogue constants) | Docs/debug only — **not** security identifiers |
| **Telemetry scrubbing** | [`tools/security/advanced_routine.py`](../../tools/security/advanced_routine.py), optional **`redact_telemetry_processor`** | Logging / exports — **shared policy** when user content might appear in structured logs |

## Omissions from this map (explicit)

The following are **out of scope** for this symbol map (they would clutter or duplicate other docs):

| Omit | Reason |
|------|--------|
| **`misc/` tree** | Archived/experimental; excluded from default Ruff scope ([`pyproject.toml`](../../pyproject.toml) `extend-exclude`). Nested **`pyproject.toml`** files there are **legacy subtrees**, not the canonical Echoes package. |
| **Full HTTP route enumeration** | Prefer live OpenAPI: `uv run python -c "from api.main import app; …"` per [`CLAUDE.md`](../../CLAUDE.md); routes evolve independently of the assistant class. |
| **Raw secrets / PII in examples** | Never part of the map; use **`tools.security`** for redacted narratives. |
| **Third-party MCP servers & IDE bridges** | Operational context only — not Python import surfaces in this repo. |
| **Legal/consent copy text** | Behavioral contracts live in legal modules; not duplicated here. |

## Inheritance (MRO)

```text
EchoesAssistantV2 → KnowledgeGraphMixin → MultimodalMixin → LegalAccountingMixin → QuantumStateMixin → DirectoryAnalysisMixin → object
```

Docstring in-class ordering matches mixin responsibilities (knowledge + multimodal ordering is intentional).

| Mixin | Module | Role |
|-------|--------|------|
| KnowledgeGraphMixin | [`core_modules/knowledge_graph_mixin.py`](../../core_modules/knowledge_graph_mixin.py) | Knowledge graph CRUD, memory fragments, contextual chat |
| MultimodalMixin | [`core_modules/multimodal_mixin.py`](../../core_modules/multimodal_mixin.py) | Multimodal files, resonance |
| LegalAccountingMixin | [`core_modules/legal_accounting_mixin.py`](../../core_modules/legal_accounting_mixin.py) | Consent, cognitive accounting |
| QuantumStateMixin | [`core_modules/quantum_state_mixin.py`](../../core_modules/quantum_state_mixin.py) | Quantum state persistence |
| DirectoryAnalysisMixin | [`core_modules/directory_analysis_mixin.py`](../../core_modules/directory_analysis_mixin.py) | Directory / codebase analysis (uses `chat.completions` internally) |

## Co-located types in `assistant_v2_core.py` (same file)

| Symbol | Kind | Purpose |
|--------|------|---------|
| `ContextManager` | class | Session-scoped message list + `utc_now_iso_ms` timestamps |
| `MemoryStore` | class | JSON persistence under `data/memory` |
| `interactive_mode` | function | CLI loop; constructs `EchoesAssistantV2(...)` |

## Construction graph (major collaborators)

These are attached on `self` during `EchoesAssistantV2.__init__` (see ~481–780+):

| Attribute / area | Source module | Notes |
|------------------|---------------|-------|
| `client` | `openai.OpenAI` | Sync client; API key from env |
| `model_router`, `response_cache`, `model_metrics` | [`app/model_router.py`](../../app/model_router.py) | Routing + cache + metrics |
| `context_manager`, `memory_store` | Same file (`ContextManager`, `MemoryStore`) | |
| `tool_registry` | [`tools/registry.py`](../../tools/registry.py) | Optional tools |
| `action_executor` | [`app/actions`](../../app/actions) | |
| `knowledge_manager` | [`app/knowledge`](../../app/knowledge) | |
| `fs_tools` | [`app/filesystem`](../../app/filesystem) | |
| `agent_workflow` | [`app/agents`](../../app/agents) (`AgentWorkflow`) | |
| `quantum_state_manager` | `misc/quantum_state/...` | Optional |
| `rag` | RAG factory when enabled | |
| `value_system` | [`app/values`](../../app/values) | Optional |
| `knowledge_graph` | [`knowledge_graph`](../../knowledge_graph) | Optional |
| `multimodal_engine` | multimodal resonance | Optional |
| `legal_system`, `accounting_system` | legal / accounting packages | Optional |
| `glimpse_engine` | [`glimpse`](../../glimpse) | Preflight / clarifiers |
| `parallel_simulation` | [`core_modules/parallel_simulation_engine.py`](../../core_modules/parallel_simulation_engine.py) | Module singleton, not per-instance |

## Global engines / singletons (import-time)

Used by chat and cognition paths; not attributes of the instance but tightly coupled:

| Symbol | Module |
|--------|--------|
| `intent_engine` | [`core_modules/intent_awareness_engine.py`](../../core_modules/intent_awareness_engine.py) |
| `thought_tracker` | [`core_modules/train_of_thought_tracker.py`](../../core_modules/train_of_thought_tracker.py) |
| `cross_reference_system` | [`core_modules/cross_reference_system.py`](../../core_modules/cross_reference_system.py) |
| `catch_release` | [`core_modules/catch_release_system.py`](../../core_modules/catch_release_system.py) |
| `humor_engine`, `personality_engine` | humor / personality modules |
| `parallel_simulation` | parallel simulation engine |

## Public / semi-public methods on `EchoesAssistantV2` (representative)

Grouped for v1 extraction; line numbers are approximate (`assistant_v2_core.py`).

| Group | Methods |
|-------|---------|
| Chat | `chat`, `_chat_nonstreaming`, `_chat_streaming`, `get_conversation_history`, `provide_feedback` |
| API bridging | `_convert_tools_to_responses_format`, `_convert_to_responses_input`, `_convert_to_chat_messages` |
| Context | `update_context`, `get_context`, `get_context_summary`, `save_context`, `load_context`, `_retrieve_context` |
| Tools | `_execute_tool_call`, `_improve_response`, `list_tools` |
| Knowledge / RAG | `add_knowledge`, `gather_knowledge`, `search_knowledge` |
| Files / workflows | `list_directory`, `get_directory_tree`, `read_file`, `write_file`, `search_files`, `run_workflow` |
| ROI / business | `store_roi_analysis`, `search_roi_analyses`, `get_roi_summary`, `organize_roi_files` |
| Ops | `get_stats`, `get_action_history`, `get_action_summary`, `print_model_metrics`, `reset_model_metrics` |
| Glimpse | `enable_glimpse_preflight`, `set_glimpse_anchors`, `commit_glimpse` |
| Legal / compliance | `create_user_consent_agreement`, `generate_user_financial_statement`, `verify_license_compliance`, `get_legal_accounting_statistics`, `_check_*` helpers |

## Related agent-layer types (outside `EchoesAssistantV2`)

| Symbol | Location | Relation |
|--------|----------|----------|
| `Agent`, `ConversationHistory`, `Message` | [`app/agents/models.py`](../../app/agents/models.py) | Separate async agent path (`chat.completions`); not merged with EchoesAssistantV2 |
| `AgentWorkflow` | [`app/agents/agent_workflow.py`](../../app/agents/agent_workflow.py) | Holds reference to assistant |

## Graduation risks / checklist for `EchoesAgentsV1`

1. **Split transport:** isolate OpenAI `responses.create` vs `chat.completions.create` behind one façade (see [`docs/MIGRATION_OPENAI.md`](../../docs/MIGRATION_OPENAI.md)).
2. **Singleton vs DI:** `thought_tracker`, `parallel_simulation`, etc. complicate multi-tenant or parallel tests — consider injection for v1.
3. **File size:** `assistant_v2_core.py` is a monolith — extract chat pipeline, tool loop, and compliance into packages when naming `echoesagentsv1`.
4. **Tests:** [`tests/test_echoes_assistant_v2_comprehensive.py`](../../tests/test_echoes_assistant_v2_comprehensive.py), [`tests/test_agentic_assistant.py`](../../tests/test_agentic_assistant.py), demos under [`demos/`](../../demos/).

## Motivation layer (Pink Floyd) — explicit catalogue

Canonical tokens and URLs live in [`core_modules/motifs.py`](../../core_modules/motifs.py). Track list for this audit:

1. **Echoes** — namesake of the platform and long-form continuity.
2. **Shine On You Crazy Diamond** — persistence / return (already encoded as `SHINE_ON_YOU_CRAZY_DIAMOND`).
3. **Welcome to the Machine** — external systems / tool-and-MCP “machine hallway”; URL stored as constant (see motifs).
4. **High Hopes** — “sound meets cognition”: proposed graduate hook for an `Abrasive` motif type (texture of intervention / closing-arc energy). **There is no legacy `@abrasive` symbol in the repo** — the dataclass in `motifs.py` is an intentional anchor for v1 design discussion, not wired into `EchoesAssistantV2`.

---

*Generated for graduation planning; update when large refactors land.*
