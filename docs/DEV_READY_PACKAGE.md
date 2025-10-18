# Realtime Preview — Development-Ready Research Package

## Purpose
Specify functional/architectural requirements and stable interfaces for integration from `D:\realtime` into host applications.

## Core Requirements
- **Language**: Python 3.8+
- **Dependencies**: None (standard library only)
- **Security**: Optional integration with `D:\thon.py`; otherwise fallback security active
- **Performance**: Real-time on rolling windows (default: points=100, events=50)
- **Persistence**: JSON exports for state and animations

## Public Interfaces (stable)

### `realtime_preview.RealtimePreview`
- `start() -> bool`
- `stop() -> None`
- `process_input(action: str, **kwargs) -> Dict[str, Any]`
  - actions: `insert(position:int, text:str)`, `delete(start:int, end:int)`, `replace(start:int, end:int, text:str)`, `undo()`, `redo()`
- `get_current_preview() -> Optional[str]` (ASCII)
- `get_full_state() -> Dict[str, Any]`
- `set_visualization_mode(mode: str) -> bool`  // `timeline|tree|flow|heatmap`
- `export_session(output_dir: str) -> None`
- `clear_all() -> None`

### `core_trajectory.TrajectoryEngine`
- `register_analyzer(fn: List[TrajectoryPoint] -> TrajectoryDirection) -> None`
- `add_point(content: str, metadata: Optional[Dict]) -> TrajectoryPoint`
- `predict_next_states(lookahead: int = 3) -> List[Dict]`
- `get_current_state() -> Dict`
- `get_trajectory_summary() -> Dict`
- `export_trajectory(filepath: str) -> None`

### `input_adapter.InputAdapter`
- `register_suggestion_provider(fn: AdaptationContext -> List[str]) -> None`
- `process_insert(position: int, text: str) -> InputEvent`
- `process_delete(start: int, end: int) -> InputEvent`
- `process_replace(start: int, end: int, text: str) -> InputEvent`
- `undo() -> Optional[InputEvent]`
- `redo() -> Optional[InputEvent]`
- `get_adaptation_context() -> AdaptationContext`
- `compute_diff(other_content: str) -> List[str]`

### `visual_renderer.VisualRenderer`
- `set_mode(mode: VisualizationMode) -> None`
- `render(trajectory_data: Dict, input_context: Optional[Dict]) -> PreviewFrame`
- `export_animation(filepath: str, frame_limit: Optional[int]) -> None`
- `generate_ascii_preview(frame: PreviewFrame, width: int = 80, height: int = 20) -> str`

### `security_integration.SecurityManager`
- `run_security_check() -> bool`
- `assess_security_context() -> SecurityContext`
- `validate_operation(operation: str) -> bool`
- `validate_command(command: str) -> Dict[str, Any]`
- `get_security_metrics() -> Dict[str, Any]`
- `export_security_report(filepath: str) -> None`

## Configuration Contract
`PreviewConfiguration` keys (see `realtime_preview.py`):
- `visualization_mode: str`
- `enable_security: bool`
- `enable_predictions: bool`
- `enable_suggestions: bool`
- `trajectory_window_size: int`
- `input_buffer_size: int`
- `auto_save_interval: float`

## Integration Patterns
- **In-process plugin**: Import and embed `RealtimePreview` in host process; wire editor events to `process_input()`.
- **Sidecar service**: Thin local process; host sends events (e.g., stdin/stdout or IPC); returns preview + trajectory JSON.

## File I/O Conventions
- Exports under `exports/` subfolders or explicit `output_dir`.
- Autosave under `autosave/` with timestamped `trajectory_*.json`, `animation_*.json`.

## Security & Safety
- Always check `SecurityManager.validate_operation()` before `export_session()` in production contexts.
- Use fallback security if `D:\thon.py` is unavailable (already implemented).

## Readiness Checklist
- [x] Stable APIs documented
- [x] Demo coverage for text and code
- [x] Test suite for core components
- [x] Security integration and fallbacks
- [x] Pure Python portability

## Handoff Artifacts
- This document
- `RESEARCH_CHARTER.md`, `APPLICATIONS_MAP.md`, `PROTOTYPE_REPORT.md`, `RD_ROADMAP.md`, `ADAPTIVE_INTELLIGENCE_BLUEPRINT.md`
