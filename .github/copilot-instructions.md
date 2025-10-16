## Quick instructions for AI coding agents

This file provides essential guidance for AI coding agents working in this repository.

### Big-picture architecture
- Modular agent architecture with three key components:
  1. Architect agent for design and planning
  2. Reviewer agent for validation
  3. Tester agent for verification

- Smart context retention system maintains analytical memory across sessions:
  - Persistent memory storage in `memory.json` with insights, patterns and preferences
  - Session-based context tracking with configurable retention policies
  - Cross-session learning capabilities for continuous improvement
  - Automatic insight synthesis and pattern recognition
  - Semantic reasoning for context-aware responses

- Unified configuration management:
  - Centralized config through `packages/core/config/__init__.py` using pydantic-settings
  - Environment-specific settings with validation (.env, dev, prod)
  - Secure secrets management with rotation support
  - Configuration inheritance and override capabilities
  - Runtime configuration updates and validation

- Hybrid operation support:
  - Seamless routing between OpenAI/Azure/Local providers
  - Automatic failover and load balancing
  - Provider-specific optimizations
  - Configurable model selection and routing rules
  - Local fallback for offline operation

- Comprehensive security validation:
  - Multi-layer security checks with cross-agent validation
  - Endpoint vulnerability protection with vector analysis
  - Security scanning and penetration testing
  - Secrets and credentials protection
  - Rate limiting and access control
  - Audit logging and compliance monitoring

### Key files and components
- `packages/core/config/__init__.py` - Central configuration using pydantic-settings
- `ai_agents/orchestrator.py` - OpenAI Agents SDK orchestration with handoffs and rate limiting
- `ai_modules/minicon/config.py` - Agent configuration and API key management
- `automation/backend/assistant_api.py` - FastAPI service for agent coordination
- `packages/security/*` - Security validation layers and compliance checks
- `packages/monitoring/*` - Performance tracking and analytics
- `packages/core/` - Shared utilities and base functionality
- `workflows/macro.py` - Parallel workflow execution and deterministic merging
- CI workflow: `.github/workflows/integration-windows.yml` - Runs comprehensive test suite

### Endpoint contract (use this in tests and examples)
- POST /transform
  - Request JSON: { "text": "<string>" }
  - Local deterministic response when OPENAI_API_KEY is empty: `{"result":"[local-echo] <reversed text>"}`
  - Example: POST {"text":"abc"} -> `"[local-echo] cba"`

### Smart Context Retention System
The system uses a sophisticated context management approach:

1. Memory Components:
   - Insights: Learned patterns and observations with confidence scores
   - User Preferences: Persistent user-specific settings and preferences
   - Project Metrics: Codebase analysis and project performance data
   - Successful Strategies: Record of effective problem-solving approaches

2. Context Management:
   - Session tracking with unique IDs and timestamps
   - Cross-session memory persistence via `memory.json`
   - Automatic insight synthesis from feedback loops
   - Semantic reasoning for context-aware responses

3. Performance Optimization:
   - Cache management (max 1000 insights)
   - Confidence-based insight prioritization
   - Query-relevant context retrieval
   - Semantic pattern matching

4. Key Files:
   - `prompting/core/context_manager.py`: Core context management
   - `prompting/core/insight_synthesizer.py`: Insight generation and integration
   - `knowledge_graph/system.py`: Semantic reasoning capabilities
   - `memory.json`: Persistent storage for cross-session retention

### Developer workflows (concrete commands)
- Create venv, install, run service (PowerShell):
  - cd python; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; .\.venv\Scripts\python.exe -m uvicorn service:app --host 127.0.0.1 --port 8000
- Run the deterministic integration test (idempotent): `.\integration_test.ps1` from repo root. It ensures `OPENAI_API_KEY` is unset for deterministic output.
- Build/run C# (from `csharp` folder): `dotnet build` then `dotnet run --project .` (adjust depending on your local layout).
- Full end-to-end (Windows): run `.
un_bundle.ps1` — convenient but opaque; inspect `run.log` for symptoms.

### Project-specific conventions

#### Configuration Management
- Environment variables prefixed with `ECHO_` in pydantic settings
- Configuration validation through Pydantic models
- Environment-specific config files (.env.development, .env.production)
- Secure defaults with overridable settings
- Dynamic config reloading support
- Hierarchical settings inheritance

#### Security Architecture
- Security validations must cross-validate between agents
- Comprehensive vulnerability scanning
- API keys managed through primary/secondary system with rotation
- Endpoint protection using vector analysis
- Secure production deployment with HTTPS/TLS
- Immutable audit logging

#### Hybrid Operation
- Runtime provider switching between OpenAI/Azure/Local
- Automatic failover and redundancy
- Provider-specific configuration and optimization
- Load balancing and rate limiting
- Local fallback mechanisms
- Cross-provider compatibility

#### Best Practices
- All agents must implement context preservation and harmonic resonance
- Use trajectory testing to validate analytical consistency
- Features controlled via `.env` with detailed config options
- Monitoring setup requires proper telemetry configuration
- Regular security audits and penetration testing
- Documentation must be kept up-to-date

### Common gotchas
- Never disable `HYBRID_ASSISTANT_CROSS_VALIDATION` in production
- Agents require proper backoff config via `HYBRID_ASSISTANT_COMPLEXITY_THRESHOLD`
- Test environments must set `TESTING=true` to enable deterministic behavior
- Rate limiting is enforced at the individual agent level
- Ensure proper API key rotation and fallback configuration

### Integration points and external dependencies
- OpenAI API: optional; controlled by `OPENAI_API_KEY` with primary/secondary key support
- Azure AI: configurable through `AZURE_AI_*` settings for hybrid operation
- Logging: Uses structured logging with configurable backends
- Monitoring: Supports Datadog and custom metric endpoints
- Storage: Local SQLite by default, configurable for other databases
- Auth: JWT-based authentication with role-based access control

### Examples for common tasks
1. Add a new agent:
   - Implement in `ai_modules/`
   - Use `AgentTemplates.create_code_reviewer()`, `.create_architect()`, or `.create_test_engineer()`
   - Add configuration in `packages/core/config/__init__.py`
   - Register in `automation/backend/assistant_api.py`
   - Add validation in `packages/security/`

2. Modify routing logic:
   - Update `HYBRID_ASSISTANT_DEFAULT_STRATEGY` options
   - Adjust thresholds in `packages/core/config/__init__.py`
   - Add test cases in `test_model_integrity.py`

3. Add monitoring:
   - Define metrics in `packages/monitoring/`
   - Configure outputs in `LLM_USAGE_*` settings
   - Update dashboards in `automation/reports/`

### Common coding patterns

#### Async/Await Usage
- Use `async def` for all agent and API operations
- Implement proper error handling with `try/except Exception as e`
- Use `asyncio.gather()` for concurrent task execution
- Apply exponential backoff with jitter for rate limiting

#### Agent Orchestration
- Create agents using `AIAgentOrchestrator.create_agent()` with task_importance
- Use `gpt-4o` for "important" tasks (architect, reviewer) and `gpt-4o-mini` for "basic" tasks (tester)
- Implement handoffs between agents for collaborative workflows
- Group tasks by agent type for sequential execution

#### Workflow Patterns
- Use `macro_parallel()` from `workflows/macro.py` for concurrent layer execution
- Implement `merge_outputs()` for combining parallel results
- Follow deterministic merge rules with priority mapping
- Record merge conflicts in `reports/merge_log_YYYYMMDD.json`

#### Error Handling
- Catch broad exceptions with `except Exception as e`
- Log detailed error information including status codes and types
- Implement retry logic with exponential backoff for API failures
- Handle rate limits (429) with adaptive delays

#### Testing Conventions
- Use `def test_` naming for all test functions
- Follow pytest patterns for comprehensive test suites
- Test agent coordination and cross-validation
- Validate security and trajectory consistency
- CI enforces cross-validation between agents
- Performance tests must validate "harmonic resonance"
- Security scans check for exposed API keys and credentials
- Use `tools/purge_env_history.ps1` (dry-run) to produce commands for cleaning secrets
- For repository mirroring, see `tools/purge_repo_mirror.ps1` (use -Execute to run)

If anything in this document is unclear or outdated, tell me which file I should re-scan and I will update these instructions.

### Contract + concrete examples
- Request shape: POST /transform with JSON { "text": "..." }
- Response shape: JSON { "result": "<string>" }
- Local fallback behaviour (as implemented in `python/service.py`): when `OPENAI_API_KEY` is empty the service returns `{"result": "[local-echo] <reversed input>"}`. Example:
  - Request: { "text": "abc" }
  - Response: { "result": "[local-echo] cba" }

### Troubleshooting common failures observed during local runs
- pip access / virtualenv errors: if `pip install` fails with a FileNotFoundError while creating an access-test file, try:
  - ensure Python is installed and available on PATH
  - run the venv creation and pip install steps from an elevated PowerShell if your machine restricts filesystem access
  - manually create a `.venv` and use the system Python if virtualenv creation fails
- uvicorn not found: install `uvicorn[standard]` into the venv (`pip install -r python/requirements.txt`) or run the service with the system `python -m uvicorn` after activating the venv.

### Where to run history-purge helpers
- Use `tools/purge_env_history.ps1` to print recommended commands (dry-run).
- Use `tools/purge_repo_mirror.ps1 -RemoteUrl 'https://github.com/owner/repo.git'` to print a mirror+purge sequence; add `-Execute` only when you are ready to rewrite history and force-push.

### Developer quickstart pointers
- For a compact, copy-paste developer quickstart see `DEVELOPER_QUICKSTART.md` at the repo root.
