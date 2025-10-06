# docs/PHASE2_ORGANIZE_DECLUTTER.md

## Phase 2: Organize, Declutter, Invoke Janitor

This phase organizes the codebase for better navigation, declutters dead code, runs janitor for cleanup, upgrades janitor with contextual GC, and updates docs.

### Step 1: Organize Files and Folders
**Actions**:
- Created `configs/ai/` and moved AI-related configs (`llm_swing_profiles.yaml`, `user_profiles.yaml`).
- Created `scripts/utils/` and moved utility scripts (`evaluate_swing_profiles.py`, `demo_content_routing.py`).
**Why**: Groups related modules, simplifies structure.

### Step 2: Declutter Files
**Actions**:
- Removed unused imports (e.g., `rich.prompt.Prompt` from `tour.py`).
- Updated paths in code (e.g., `swing_scheduler.py` to `configs/ai/`).
**Why**: Cleaner code, fewer lints.

### Step 3: Invoke Janitor.py --consolidate
**Actions**:
- Ran `python janitor.py --consolidate`.
- Cleaned `__pycache__` dirs and temp files.
**Why**: Keeps repo clean.

### Step 4: Upgrade Janitor.py
**Actions**:
- Added `add_contextual_cleanup()` method:
  - Removes logs older than 30 days.
  - Archives large files (>10MB) in `content/` to `archive/large_files/`.
  - Cleans invalid venv dirs.
**Why**: More context-aware garbage collection.

### Step 5: Update Documentations
**Actions**:
- Created this doc `docs/PHASE2_ORGANIZE_DECLUTTER.md`.
**Why**: Documents the phase.

### Files Modified/Added
- **Moved**: `configs/llm_swing_profiles.yaml`, `configs/user_profiles.yaml` → `configs/ai/`.
- **Moved**: `scripts/evaluate_swing_profiles.py`, `scripts/demo_content_routing.py` → `scripts/utils/`.
- **Modified**: `app/harmony/swing_scheduler.py`, `app/cli/tour.py`, `janitor.py`.
- **Added**: `docs/PHASE2_ORGANIZE_DECLUTTER.md`.

All phases complete. Ready for next development cycle. Test suite passes, docs updated. Repo organized and clean.
