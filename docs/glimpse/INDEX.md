# Glimpse Realtime — Documentation Index

This is the canonical entry point for all Glimpse realtime documentation. It provides a context-aware map to architecture, pipelines, integrations, deployment, and client usage.

---

## 1) Overview
- **Product intro and architecture summary:** `README.md`
- **When to use:** Real-time preview and trajectory analysis for text/code with optional security guardrails and HITL augmentation.

---

## 2) Architecture & Components
- **System integration (SSE + wiring):** `SYSTEM_INTEGRATION.md`
  - Covers `server_sse.py` endpoints (`POST /input`, `GET /events`, `GET /health`)
  - Explains orchestration via `GlimpseOrchestrator` and component responsibilities
- **Core modules referenced**
  - `realtime_preview.py` — orchestrator lifecycle and callbacks
  - `input_adapter.py` — event processing, undo/redo, suggestions
  - `core_trajectory.py` — direction/confidence analysis and segments
  - `visual_renderer.py` — timeline/tree/flow/heatmap rendering
  - `security_integration.py` — runtime guardrails, shield factor

---

## 3) Implementation Details & Extensions
- **Extension recipes and client integrations:** `EXTENSION_EXAMPLES.md`
  - Custom `InputAdapter` (e.g., Markdown-aware)
  - Custom trajectory analyzers (e.g., code complexity)
  - Custom renderers (e.g., Mermaid diagrams)
  - Security validator patterns
  - Full integration example (code review system)
  - JavaScript and Python client examples for SSE

---

## 4) Instruction Pipeline (Profiling Targets)
- **End-to-end flow and key stages:** `INSTRUCTION_PIPELINE.md`
  - Input reception → orchestration → trajectory update → rendering → broadcast
  - Performance considerations and debugging tips
  - Stage-level metrics to capture (latencies, throughput, buffers)

---

## 5) Deployment & Operations
- **Optimization, security, monitoring, and rollout:** `DEPLOYMENT_AND_OPERATIONS.md`
  - Performance tuning (GC, memory caps, stage-latency metrics)
  - Security (validation, rate limiting, auth, permissions)
  - Monitoring and maintenance (alerts, logs, error tracking)
  - Deployment checklist and future roadmap

---

## 6) Clients
- **JavaScript SSE client:** see `EXTENSION_EXAMPLES.md` (Client-Side Integration → JavaScript SSE Client)
- **Python SSE client:** see `EXTENSION_EXAMPLES.md` (Python Client)
  - Optional install:
    - `pip install -r requirements/clients.txt`

---

## 7) Notebooks (Analyses)
- `notebooks/instruction_pipeline_analysis.ipynb`
- `notebooks/realtime_analysis.ipynb`

Use these to validate pipeline behavior, measure latency distributions, and visualize system dynamics under different workloads.

---

## 8) Related Docs (Cross-Project)
- `docs/CROSS_PLATFORM_INTEGRATION.md` — platform connectors and bridges
- `docs/HITL_Operator_Guide.md` / `docs/HITL_KPI_Report.md` / `docs/HITL_Stakeholder_Summary.md` — HITL middleware suite
- `docs/HEALTH_MONITOR_README.md` — health monitoring guidelines
- `docs/ARCHITECTURE.md` — broader system architecture context

---

## 9) Quick Links
- Architecture summary → `README.md`
- SSE and wiring → `SYSTEM_INTEGRATION.md`
- Pipeline details → `INSTRUCTION_PIPELINE.md`
- Extensions and clients → `EXTENSION_EXAMPLES.md`
- Deployment & Ops → `DEPLOYMENT_AND_OPERATIONS.md`
