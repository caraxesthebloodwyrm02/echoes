# docs/PHASE1_SWING_SAMPLER.md

## Phase 1: AI Swing Sampler Architecture

This phase implements a rhythmic quantization system for LLM sampling, translating musical swing and grid logic into per-token controls for tour-guide behavior.

### Purpose
- Enable non-monotonic, natural LLM generation using swing cycles (4-beat, 6-cycle variation).
- Integrate with user personas for production-safe content creation and publishing.
- Provide analytics, evaluation, and guardrails for continuous improvement.

### Step 1: Add Config Files
**What**: Created `configs/llm_swing_profiles.yaml` and `configs/user_profiles.yaml`.
**Why**: Centralizes sampling schedules and persona definitions.
**Files Added**:
- `configs/llm_swing_profiles.yaml`: Profiles like `swing_default` with base params, swing/variation, flip rules, precision modes.
- `configs/user_profiles.yaml`: Personas like "researcher", "creator" with skill levels, modules, guardrails, preferred profiles.

### Step 2: Implement Scheduler Module
**What**: Added `app/harmony/swing_scheduler.py` with `SamplerState` class and `next_params()` method.
**Why**: Computes per-token sampling params based on state (precision, mode, direction) and rhythmic modifiers.
**Key Features**:
- Loads configs from YAML.
- Applies swing (4-beat), variation (6-cycle), downshift, re-quantize.
- Handles flips on boundaries.
- Clamps params to safe ranges.

### Step 3: Wire CLI/API for Tour-Guide
**What**: Extended `app/cli/main.py` to mount `tour` sub-app; added `app/cli/tour.py`.
**Why**: Provides user commands for onboarding, generation, publishing.
**Commands**:
- `tour onboard --user <user> --profile <profile>`: Saves user profile.
- `tour generate --user <user> --goal <goal> --max-tokens <n>`: Generates content with swing scheduler.
- `tour publish --user <user> --content-path <path> --platform <platform>`: Publishes via highway router.

### Step 4: Instrument Analytics
**What**: Modified `app/cli/tour.py` to log metadata/ratings to `automation/reports/`; added `docs/analytics_queries.md`.
**Why**: Tracks performance for iteration.
**Files Added**:
- `docs/analytics_queries.md`: Example Python queries for metrics (generation, compliance, publishing).

### Step 5: Prototype Evaluation Loop
**What**: Created `scripts/evaluate_swing_profiles.py` to simulate generation and report averages.
**Why**: Tests profiles for safety and effectiveness.
**Output**: Saves report to `automation/reports/swing_profile_evaluation.yaml`.

### Step 6: Guardrail Integration
**What**: Added `app/domains/research/guardrails.py` and `app/domains/content/guardrails.py`.
**Why**: Enforces persona-specific prompts, refusals, tone.
**Files Added**:
- Persona guardrails with templates, patterns, guidelines.

### Tests
**Files Added**:
- `tests/unit/test_swing_scheduler.py`: Tests initialization, params, flips, swing/variation.
- `tests/integration/test_tour.py`: Tests CLI commands (onboard, generate, publish).
**Results**: All tests pass (pytest exit code 0).

### Files Modified/Added Summary
- **Added**: 6 config/test/script files, 3 domain files, 2 doc files.
- **Modified**: `app/cli/main.py`, `app/cli/tour.py`, `app/harmony/swing_scheduler.py`.

### Next: Phase 2 (Organization and Decluttering)
- Organize files/folders, declutter, invoke janitor.py, upgrade script, update docs.
