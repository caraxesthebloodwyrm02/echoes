# Realtime Preview — Adaptive Intelligence Blueprint

## Goal
Equip the research space to monitor and interpret itself, producing a self-improving system.

## Telemetry Sources
- `RealtimePreview.get_full_state()` snapshots (events, directions, health, velocity, intensity)
- `autosave/trajectory_*.json`, `animation_*.json`
- `SecurityManager.export_security_report()` outputs

## Dashboards (lightweight, file-based)
- **Session Overview**: events/time, health trend, dominant directions
- **Mode Effectiveness**: outcome metrics by visualization mode
- **Security Posture**: shield factor histogram, allowed operation distribution

## Learning Loops
- **Analyzer Tuning**: adjust thresholds based on observed consistency/variance distributions
- **Suggester Refinement**: track suggestion acceptance proxies (reduced undo/delete after suggestion)
- **Window Sizing**: adapt `trajectory_window_size` and `input_buffer_size` for workload patterns

## Automation Scripts (proposed)
- `analyze_sessions.py` (future): parse exports and autosaves into summary CSV/JSON without external deps
- `report_security.py` (future): aggregate shield/risk over time

## Governance
- Store outputs under `exports/analytics/` with timestamped files.
- No external dependencies; pure Python scripts for analysis.
- Respect security gating; only read and aggregate local JSON.

## KPIs
- **Interpretability Gain**: Δ in comprehension speed vs. baseline
- **Error Reduction**: Δ corrections/100 edits
- **Stability**: average `trajectory_health` over sessions
- **Safety**: mean shield factor; fraction of blocked operations
