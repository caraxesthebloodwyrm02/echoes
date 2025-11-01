# Executive Summary — Research-Lab Macro Pipeline v3.0

**Key insight (one line):** Converge simulation (Kalman + Head-Sweep + Steam-Glimpse) and cognitive workflows (Pause Semantics + Prompt Chaining) under a single macro-orchestration that guarantees reproducibility, observability, and deterministic merges.

## Purpose

Provide a concise operational plan and a technical ledger to run, evaluate, and package experiments across physical and conversational domains. Designed for rapid iteration, auditability, and parallel expert workflows.

## What we deliver

* A reproducible harness that runs domain experiments (`demo/` + `speech/`).
* Macro orchestration (`workflows/macro.py`) that executes phases A→D and merges artifacts deterministically.
* Instrumentation and schemas for raw data, annotations, and merged outputs.
* CI gates for formatting, testing, and schema validation.
* Packaged deliverable (`deliverable_snapshot.zip`) with docs, tests, and sample datasets.

## Core components (short)

* **Simulation**: `demo/kalman.py`, `demo/headsweep.py`, `steam_glimpse_dynamics/`
* **Cognitive**: `speech/pause_model.py`, `caching/prompt_engine.py`, `templates/prompts.json`
* **Orchestration**: `workflows/macro.py` (Phase A–D runners, combiner)
* **Instrumentation**: `instrument/` (CSV/JSON outputs, metadata)
* **Tests & CI**: `tests/`, `.github/workflows/build-and-test.yml`, `tools/format_all.py`

## Immediate priorities (what to do now)

1. Normalize repo layout and enforce pre-flight (format + test).
2. Implement minimal runnable harness for Kalman and Head-Sweep.
3. Implement pause semantics skeleton and prompt cache MVP.
4. Implement macro orchestrator and deterministic combiner.
5. Add CI gates and produce the zip deliverable.

## Risks & unknowns

* **Data schema mismatches** between domains (coordinate frames, sampling rates): *Unknown* until we inspect sample runs.
* **Binary dependencies or compiled extensions**: if present, source zip will not reproduce builds.
* **Labeling consistency** for pause semantics across annotators: requires QA cycles.

## Decision points

* Choose canonical coordinate frame for physical experiments (ENu vs NED vs local).
* Confirm whether to include compiled artifacts in the deliverable.
* Acceptance criteria for pause detection and macro merge stability.
