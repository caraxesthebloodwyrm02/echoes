# Execution and Script Safety

This document defines scope and safety rules for code execution and scripts in the Echoes codebase.

## Reconstruction protocols and `compile(..., "exec")`

Scripts under `scripts/` that use `compile(content, ..., "exec")` or dynamic code execution (e.g. `reconstruction_protocol_step*.py`, `reconstruction_protocol_final_steps.py`, `validate_phase3.py`) are **controlled/admin-only**:

- **Do not** expose these scripts to user input or LLM-generated content.
- **Do not** invoke them from API routes or session handlers without an explicit admin or operator action.
- Run them only in controlled environments (CLI by an operator, CI, or admin-only tooling).
- When adding new scripts that use `compile` or `exec`, restrict execution to allowlisted inputs or admin-only entry points.

## Subprocess and tool execution

- Tool execution is routed through the **tool gate** (`tools.safe_dispatch_tool` / `execute_tool`): allowlist, payload validation, and audit logging. See `tools/__init__.py`.
- Do not run subprocesses with `shell=True` from user or LLM content; use argument lists and `shell=False`.
- For scripts that must run external commands, use an allowlist of commands and avoid passing user-controlled strings into the command line.

## Summary

| Context | Rule |
|--------|------|
| Reconstruction / `compile` scripts | Admin-only or controlled CLI; never from user/LLM flow |
| Tool dispatch | Use tool gate (allowlist + audit) |
| Subprocess | No `shell=True`; allowlist commands when possible |
