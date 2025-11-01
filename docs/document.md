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

---

# Technical Log — recent actions, artifacts, and instructions

> This ledger records executed/required tasks, file paths to create, and commands. Use as a chronological runbook for devs and agents.

## A. Repo normalization (to run now)

* Ensure repository root contains: `demo/`, `speech/`, `workflows/`, `instrument/`, `tests/`, `docs/`, `data/`, `scripts/`.
* Add `tools/format_all.py` and pre-commit config.

**Commands:**

```bash
# format and check
black . && isort . && autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r .
pre-commit run --all-files
pytest -q
```

**Notes:** Remove nested `.git` folders before staging (pre-commit hook available).

## B. Minimal harness files (create)

* `demo/kalman.py` — pure-Python Kalman filter wrapper with CLI `--input` `--output`.
* `demo/headsweep.py` — generator: `generate_head_sweep(n, noise, frame)` returns JSON `{"t":[], "measurement":[], "meta":{}}`.
* `scripts/run_all.py` — entrypoint to run `kalman` / `headsweep` / `pause` or `compare` modes.

**Test:** `tests/test_kalman_vs_head.py` (already drafted) must pass.

## C. Pause semantics & prompt cache (create)

* `speech/pause_model.py` — feature extractor: prosody (pitch, energy), inter-word gaps, filler detection. Output schema: `{timestamp, pause_type, prosody, sentiment_shift}`.
* `caching/prompt_engine.py` — store prompt-atoms with similarity & quality scores. API: `store(prompt, score)`, `retrieve(context, k)`, `chain(prompts)`.

**Data ingestion:** `data/podcasts/` with sample JSONL per episode; include 1 JRE and 1 Lex snippet as pilot.

## D. Macro orchestration

* `workflows/macro.py` — orchestrates Phase A–D:

  * Phase A: run simple baselines (Kalman, pause baseline).
  * Phase B: enrichment (headsweep outputs, prosody features).
  * Phase C: patching via prompt-Glimpse / mid-tier corrections.
  * Phase D: final large-model polish + deterministic merge.

**Combiner rule (deterministic):** merge artifacts by timestamp; on conflict, use `priority_map = {phaseD:3, phaseC:2, phaseB:1, phaseA:0}` and apply the artifact with the highest priority. Record all overwrites in `reports/merge_log_YYYYMMDD.json`.

## E. Instrumentation & schemas

* Canonical schemas in `packages/core/schemas.py` for `Measurement`, `PauseAnnotation`, `PromptChain`, `MacroArtifact`.
* All runs write `{artifact_id}.json` with metadata `{run_id, phase, timestamp, sha}`, and a content pointer.

## F. Tests & CI

* Add `tests/test_pause_model.py`, `tests/test_prompt_cache.py`, `tests/test_macro_merge.py`.
* CI job names: `python-format-lint`, `pytest`, `json-schema`.

**CI snippet (example):**

```yaml
jobs:
  python-format-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run formatter
        run: python tools/format_all.py && git diff --exit-code
```

## G. Packaging

* Composition: `demo/`, `speech/`, `workflows/`, `tests/`, `docs/`, `data/samples/`, `scripts/run_all.py`, `AGENT_TASKS.md`, `LICENSE`, `requirements.txt`.

**Command:**

```bash
zip -r deliverable_snapshot.zip demo speech workflows tests docs data scripts AGENT_TASKS.md LICENSE requirements.txt
```

---

# Appendices: Immediate file templates (short)

## 1. `AGENT_TASKS.md` (summary)

* Run pre-flight.
* Create branch `feat/macro-run-YYYYMMDD`.
* Implement file X, run tests, push PR with `pytest` logs attached.
* If schema diff appears, attach `reports/merge_log` and notify Data QA.

## 2. `reports/macro_run_YYYYMMDD.md` (template)

* Header: run_id, author, phases executed, commit sha.
* Summary table: artifacts produced, metrics, conflicts.
* Link to `data/` artifacts and `reports/merge_log.json`.

---

# Actionable next steps (choose one or more)

1. I generate the **`workflows/macro.py`** skeleton (Phase orchestrator).
2. I generate the **`AGENT_TASKS.md`** (complete).
3. I generate the **`speech/pause_model.py`** skeleton and **`caching/prompt_engine.py`**.
4. I generate ready-to-drop **docs/EXECUTIVE_SUMMARY.md** and **docs/TECHNICAL_LOG.md** as separate files (one file now contains both; export options available).

Select which to produce next; I will create the content directly into the repo or paste into chat.
