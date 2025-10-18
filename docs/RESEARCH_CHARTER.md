# Realtime Preview — Research Charter

## Purpose
- **Define** the Realtime Preview concept as realtime interpretive visualization of evolving input–output trajectories.
- **Explain** the problem it solves: high cognitive load and delayed feedback in creative/technical workflows.
- **Set** hypotheses, research questions, success metrics, and a validation plan aligned to the code in `D:\realtime\`.

## Core Concept
- **Realtime interpretive visualization**: show where the work is heading while it is being produced.
- **Feedback-rich interface**: users see, understand, and steer trajectory as it unfolds.

## Problem Statement
- **Context latency**: Users often act without a clear view of near-future consequences.
- **Comprehension burden**: Understanding direction and impact requires manual synthesis across edits.
- **Error cost**: Late discovery of misdirection leads to rework.

## Why Now
- **Event-rich tooling**: Editors and tools expose fine-grained events suitable for realtime modeling.
- **Lightweight runtime**: This prototype is pure Python (no external deps) and can run anywhere with Python 3.8+.
- **Secure-by-default**: `security_integration.py` integrates with `D:\thon.py` to gate operations.

## Functional Layers (mapped to code)
- **Input Interpretation Layer** — `input_adapter.py`
  - Parses evolving intent from events: `process_insert()`, `process_delete()`, `process_replace()`, `undo()`, `redo()`.
  - Tracks `typing_velocity`, `edit_intensity`, and maintains `event_history`.
  - Produces `AdaptationContext` with suggestions via `register_suggestion_provider()`.
- **Trajectory Simulation Layer** — `core_trajectory.py`
  - `TrajectoryEngine.add_point()` updates state; analyzes `TrajectoryDirection` and confidence.
  - Maintains rolling window and `TrajectorySegment`s; predicts next states via `predict_next_states()`.
- **Adaptive Feedback Layer** — `visual_renderer.py` + `realtime_preview.py`
  - Renders in modes: `timeline`, `tree`, `flow`, `heatmap`.
  - Orchestrates lifecycle, auto-save, callbacks, and packaging of results (`realtime_preview.RealtimePreview`).
- **Security Layer** — `security_integration.py`
  - Assesses `SecurityContext` (shield factor, risk level, allowed ops) and validates operations/commands.

## Existing Analogues & Gap
- **Analogues**: autocomplete, inline code suggestions, live Markdown/render previews, refactoring diff tools.
- **Gap filled**: trajectory-level interpretability (direction, cause–effect chain, momentum) and preview of likely futures, integrated with security gating.

## Hypotheses
- **H1 (Speed)**: Realtime interpretability increases comprehension speed vs. baseline editing by ≥20%.
- **H2 (Errors)**: Visualized trajectory reduces corrections per 100 edits by ≥15%.
- **H3 (Clarity)**: Decision clarity self-reported score improves by ≥0.5 on a 5-point Likert scale.

## Research Questions
- **RQ1**: How does visible trajectory direction affect time-to-understanding current state?
- **RQ2**: What is the relationship between `trajectory_health` and observed error frequency?
- **RQ3**: Which modes (timeline/tree/flow/heatmap) best support different tasks (writing/coding/editing)?
- **RQ4**: How do suggestions (from `AdaptationContext`) influence corrections and velocity?

## Success Metrics (operational definitions)
- **Comprehension Speed (s/task)**: time to correctly answer questions about current state.
- **Error Rate (corr/100 edits)**: number of deletions/undos per 100 events.
- **Decision Clarity (1–5)**: post-task self-report.
- **Trajectory Health (0–1)**: `TrajectoryEngine._compute_health_score()` aggregate.
- **Velocity (chars/s)**: `InputAdapter.get_typing_velocity()`.
- **Intensity (edits/s)**: `InputAdapter.get_edit_intensity()`.

## Measurement Plan
- Use `verify.py`, `demo_text_editor.py`, `demo_code_editor.py` to generate logs.
- Record per-session metrics via `RealtimePreview.get_full_state()` and autosave exports in `D:\realtime\autosave/` and `exports/`.
- Aggregate: mean, median, variance; compare to baseline runs without preview (security off, suggestions off) when needed.

## Experimental Design
- **Within-subjects**: same user performs comparable tasks with/without realtime preview.
- **Counterbalanced**: alternate condition order.
- **Tasks**: short writing, refactoring, and editing tasks bundled in demos.
- **Data**: `total_events`, `current_direction`, `confidence`, `trajectory_health`, velocity, intensity, suggestions count.

## Risks & Mitigations
- **R: Overfitting to demo tasks** → **M: diversify tasks and content**.
- **R: Misinterpret security signals** → **M: always log `SecurityContext` and reason strings**.
- **R: UI bias** → **M: evaluate multiple visualization modes per task**.

## Acceptance Criteria
- All hypotheses evaluated with collected metrics and reported in `PROTOTYPE_REPORT.md`.
- Applications map produced with feasibility and impact ranking.
- Development-ready interfaces documented for handoff.
