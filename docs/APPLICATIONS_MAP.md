# Realtime Preview — Applications Map

## Overview
Mapping domains, micro/macro applications, impact, feasibility, scalability, and integration notes grounded in `D:\realtime\` modules.

## Domains and Scenarios

| Domain | Micro-level Tool | Macro-level System | Impact Potential | Technical Feasibility | Scalability | Integration Notes |
|---|---|---|---|---|---|---|
| Creative Writing | Editor plugin that previews narrative trajectory as you type | Story development environment with live cause–effect storyline maps | High (reduces writer’s block, improves structure) | High (use `demo_text_editor.py` + `realtime_preview.py`) | Medium (per-writer local; multi-user later) | Use `InputAdapter` for events; `TrajectoryEngine` for direction; `VisualRenderer.TIMELINE` for arcs; export via `RealtimePreview.export_session()` |
| Software Development | IDE widget showing code change momentum and refactor heat | Refactoring cockpit that visualizes module-level change flows | High (clarity during refactor; fewer regressions) | High (use `demo_code_editor.py` + custom analyzers) | Medium–High (project-scale summaries) | Register analyzers via `TrajectoryEngine.register_analyzer()`; `VisualizationMode.HEATMAP` for edit hotspots |
| Debugging | Live preview of execution path deltas from edits | Interactive debugger overlay showing predicted impact regions | Medium–High | Medium (extend event model) | Medium | Use `InputAdapter.compute_diff()` to track deltas; render predicted hotspots via `VisualRenderer` |
| Education (STEM) | Concept trajectory previewer during solution steps | Interactive learning space visualizing student approach patterns | High (accelerates comprehension) | Medium–High (adapt demos) | High (classroom deployment) | Use `Preview.get_full_state()` metrics (velocity, intensity); map to learning dashboards |
| Design (UX/UI) | Text-to-flow mockup of interaction paths while editing specs | Live design system with branching flows and stability indicators | Medium–High | Medium | Medium–High | Use `VisualizationMode.FLOW` for momentum; `TREE` for branching flows |
| Decision Support | Policy/strategy live what-if preview with direction/confidence | Strategy room with trajectory projections and risk overlays | High | Medium (domain models needed) | Medium–High | Replace suggestion providers with domain heuristics; keep security layer active |
| Research Authoring | Paper drafting assistant showing argument trajectory | Research workspace with cause–effect chain maps | Medium–High | High (reuse text demo) | Medium | Use cause–effect chains from `TrajectoryPoint.cause_effect_chain` |

## Impact and Feasibility Ranking
- **Impact (Top 3)**: Development Refactoring, Creative Writing, Education.
- **Feasibility (Top 3)**: Creative Writing, Code Editor, Research Authoring.
- **Scalability (Top 3)**: Education, Decision Support, Software Development (project-level).

## Integration Pipelines (per domain)
- **Creative Writing**
  - Source: keystroke/edit events → `InputAdapter`
  - Transform: `TrajectoryEngine.add_point()` → direction/confidence
  - Visualize: `TIMELINE` → ASCII or JSON frames
  - Export: `exports/text_demo/`
- **Software Development**
  - Source: IDE buffer diffs → `InputAdapter`
  - Transform: custom code analyzers → `register_analyzer`
  - Visualize: `TREE` branches + `HEATMAP` for hotspots
  - Export: `exports/code_demo/`
- **Education**
  - Source: step submissions → `process_insert/delete`
  - Metrics: velocity, intensity, trajectory_health
  - Visualize: `FLOW` for momentum understanding

## Minimal Viable Embeddings
- **Plugin form**: wrap `RealtimePreview` methods and expose `process_input()` and `get_current_preview()`.
- **Service form**: thin local process that receives edit events, responds with `preview`, `trajectory`, `suggestions`.

## Risks & Constraints
- **Event fidelity** varies across hosts; mitigate via adapter shims.
- **Security** must gate exports and command validation (`SecurityManager.validate_operation()`).
- **Performance**: keep window sizes (`trajectory_window_size`, `input_buffer_size`) tuned for host.
