# Realtime Preview — Research Prototype Report

## Objective
Evaluate interpretability and adaptability effects using the built-in demos and instrumentation in `D:\realtime`.

## Prototypes Used
- **Text Demo**: `demo_text_editor.py` (timeline mode)
- **Code Demo**: `demo_code_editor.py` (tree/heatmap modes + code analyzer)
- **Quick Verify**: `verify.py`
- **Orchestrator**: `realtime_preview.RealtimePreview`

## Experimental Design
- **Design**: Within-subjects; subjects perform comparable tasks with and without preview.
- **Counterbalance**: Alternate condition order to minimize learning effects.
- **Tasks**: short story writing, code function authoring, refactor editing.

## Metrics (captured via APIs)
- **Direction**: `TrajectoryEngine.current_direction`
- **Confidence**: `TrajectoryPoint.confidence` (recent consistency)
- **Trajectory Health (0–1)**: `TrajectoryEngine._compute_health_score()`
- **Velocity (chars/s)**: `InputAdapter.get_typing_velocity()`
- **Intensity (edits/s)**: `InputAdapter.get_edit_intensity()`
- **Suggestions Used**: count suggestions returned from `AdaptationContext`
- **Security**: `SecurityContext.shield_factor`, `risk_level`, `allowed_operations`

## Data Collection Procedure
1. Run a session (example):
   - Text demo: `python demo_text_editor.py`
   - Code demo: `python demo_code_editor.py`
2. After each task, call `system.get_full_state()` or inspect exported JSON under:
   - `D:\realtime\autosave\*`
   - `D:\realtime\exports\text_demo\` or `...\code_demo\`
3. Record per-session values: `total_events`, `trajectory.current_direction`, `trajectory.trajectory_health`, velocity, intensity.

## Analysis Plan
- Compare means between conditions (preview vs. baseline/no-preview).
- Track correlation between `trajectory_health` and error proxies (undo/delete frequency).
- Segment by visualization mode to evaluate modality fit.

## Findings (template)
- **Comprehension Speed**: [to fill] s/task; Δ vs. baseline: [to fill]%.
- **Error Reduction**: corrections/100 edits reduced by [to fill]%.
- **Decision Clarity**: Likert +Δ [to fill].
- **Mode Fit**: timeline best for [to fill]; heatmap best for [to fill].

## Qualitative Observations (template)
- **Cause–Effect Chains** helped participants explain state transitions.
- **Flow Mode** increased perceived momentum awareness.
- **Security Reports** gave users confidence in safe operations.

## Limitations
- Demos simulate editing; real host integrations may have richer events.
- Confidence heuristics are simple; ML integration left for future work.

## Next Experiments
- Add a lightweight logger that writes `get_full_state()` snapshots at intervals.
- Evaluate suggestion-provider variants per domain.

## Conclusion
The prototype substantiates the viability of realtime interpretive visualization using pure Python components, with measurable, operational metrics ready for engineering integration.
