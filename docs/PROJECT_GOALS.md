# Project Goals - Lumina Assistant

## Primary Outcomes
- Improve codebase maintainability and structure (organized modules, fewer root files)
- Enable natural language task execution as the primary workflow interface
- Integrate adaptive behavior control (Stick Shift) into all planning/execution flows
- Prepare for MCP integration (filesystem, shell, GitHub, Ollama) with a clean abstraction layer
- Establish a knowledge foundation (docs + later Knowledge Graph) for context-aware reasoning
- Ensure safety: dry-run by default, clear logging, and confirmation on destructive actions

## Quality & DX Targets
- Lint-clean (Ruff) and formatted (Black) project-wide
- Pytest green on Glimpse tests; add basic integration tests for natural language executor
- Bootstrap script validates environment and context inputs
- CI or local scripts to run lint + tests consistently

## Phase Objectives (Short-term)
1. Phase 3 (MCP Foundation)
   - Scaffold MCP client + tool registry
   - Feature-flag MCP usage in executor; fallback to local FS
   - Demo MCP filesystem operations
2. Phase 4 (Knowledge Graph - scaffold only)
   - Stubs for KnowledgeGraph and SemanticIndexer (feature-flag off)
3. Phase 5 (MOE - scaffold only)
   - Stubs for ExpertRouter and experts/* (feature-flag off)

## Success Criteria
- Natural language dry-run returns 4-phase plans consistently
- Stick Shift selects gears appropriately and logs status
- Docs and goals are fed into context prompts (previews displayed)
- Bootstrap script reports READY with all checks passing
