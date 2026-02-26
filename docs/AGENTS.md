# Echoes Agent Guide

Use this guide when working in `echoes` inside the partitioned workspace.

## Zone
- `echoes` is part of the **Common Desk** (assistant synthesis/orchestration).

## Source of truth
- For workspace policy: `VSCode-Workspace-BestPractices/AGENTS.md`
- For project behavior: `echoes` code + docs
- For contract-impacting decisions: cross-check Chamber authority (`assistive-tool-contract`, `afloat`)

## Editing rules
- Keep edits scoped to requested outcomes.
- Avoid unrelated refactors.
- Keep commands reproducible and local-first.

## Validation rules
- Run the narrowest relevant checks first.
- Report failures that are unrelated instead of silently changing broad areas.

## Handoff rules
- Summarize what changed, where, and why.
- List any assumptions or follow-ups needed.
