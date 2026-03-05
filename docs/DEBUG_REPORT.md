# Debug Report

**Purpose:** Snapshot of current test and lint state for regression tracking and delegation.  
**Contract:** See [DEBUG_CONTRACT.yaml](./DEBUG_CONTRACT.yaml) for machine-usable no-regression criteria.

---

## 1. Baseline (as of report date)

| Check | Result | Notes |
|-------|--------|--------|
| **Lint** | Pass | `ruff check` + `ruff format --check` on `api/`, `app/`, `glimpse/`, `tools/` |
| **Tests passed** | ≥ 250 | Excludes known skips and known failures |
| **Tests failed** | 8 | All in `tests/test_rag_orbit.py` (FAISSRetriever, ProvenanceTracker API) |
| **Tests skipped** | ~88 | OPENAI_API_KEY, c_o_r_e imports, matplotlib, Q4 dashboard |

---

## 2. Verification commands (run before/after any delegated work)

These commands are the source of truth for the debug contract. Run from repo root with `uv` (or `make` where available).

```bash
# Lint (must exit 0)
uv run ruff check api/ app/ glimpse/ tools/
uv run ruff format --check api/ app/ glimpse/ tools/

# Tests (baseline: ≥250 passed, 8 known failures in test_rag_orbit)
uv run pytest tests/ -q --tb=line
```

**Contract equivalence:** See `DEBUG_CONTRACT.yaml` → `verification_commands` and `baseline`.

---

## 3. Protected areas (no regression)

- **core/ethos** — `enforce()` sets env defaults; tests in `tests/test_ethos.py` must pass.
- **misc/quantum_state** — `QuantumStateManager` load_state handles empty file; tests in `tests/test_quantum_state_integration.py` must pass (import from `misc.quantum_state`).
- **src/rag_orbit/embeddings** — `embed_text` / `embed_batch` return `np.ndarray`; `tests/test_rag_orbit.py` embedding tests must pass (checksum length 32, similarity tolerance).
- **glimpse/engine** — `PERFORMANCE_AVAILABLE` / `CLARIFIER_AVAILABLE` live on `glimpse.engine`; tests in `tests/glimpse/test_coverage_completions.py` patch these and must pass.

---

## 4. Known failures (allowed in baseline; do not fix by weakening tests)

| Test(s) | Reason |
|---------|--------|
| `test_rag_orbit.py::TestFAISSRetriever::test_save_and_load` | FAISSRetriever has no `save` method |
| `test_rag_orbit.py::TestFAISSRetriever::test_get_stats` | Retriever stats shape differs (e.g. no `embedding_dim`) |
| `test_rag_orbit.py::TestProvenanceTracker::test_record_*` (6) | ProvenanceTracker does not accept `storage_path` kwarg |

Fixing these requires implementation changes (add `save`/`get_stats`, or align ProvenanceTracker constructor); do not relax or remove assertions to make them pass.

---

## 5. Delegation instructions

1. **Before starting:** Run verification commands above; record output (e.g. `pytest … > test_baseline.txt`).
2. **Use the contract:** Validate against `DEBUG_CONTRACT.yaml` (baseline counts, lint exit 0).
3. **After changes:** Re-run verification; ensure no regression (passed count ≥ baseline, same or fewer failures in protected areas).
4. **Report:** If new failures appear, list them in a short debug addendum and either fix or add to “known failures” and update the contract baseline.

---

## 6. Related docs

- [CI_RELIABILITY_CONTRACT.md](./CI_RELIABILITY_CONTRACT.md) — CI pipeline and job definitions.
- [.github/ci_reliability_contract.yaml](../.github/ci_reliability_contract.yaml) — Machine-readable CI contract.
