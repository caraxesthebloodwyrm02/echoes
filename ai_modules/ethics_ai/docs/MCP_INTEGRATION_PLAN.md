# MCP Integration - Detailed Implementation Plan

## Overview

Integrate Model Context Protocol (MCP) to enable standardized tool calling, resource access, and communication with AI Toolkit and external MCP servers.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              MCP Integration Layer                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐       │
│  │   MCP Server     │      │   MCP Client     │       │
│  │  (Expose Tools)  │      │  (Consume Tools) │       │
│  └──────────────────┘      └──────────────────┘       │
│           ↓                         ↓                   │
│  ┌──────────────────┐      ┌──────────────────┐       │
│  │  Tool Registry   │      │  AI Toolkit      │       │
│  │  (200+ tools)    │      │  MCP Servers     │       │
│  └──────────────────┘      └──────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. MCP Server (`app/mcp/mcp_server.py`)

**Purpose**: Expose assistant capabilities via MCP protocol

```python
from typing import List, Dict, Any
import asyncio
from mcp import Server, Tool, Resource

class AssistantMCPServer:
    """
    MCP server exposing assistant capabilities.
    """

    def __init__(self):
        self.server = Server("assistant-mcp")
        self.tools = self._register_tools()
        self.resources = self._register_resources()

    def _register_tools(self) -> List[Tool]:
        """Register all available tools."""
        return [
            # Code understanding
            Tool(
                name="analyze_code",
                description="Analyze code structure and semantics",
                parameters={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "language": {"type": "string"},
                    },
                },
                handler=self._analyze_code,
            ),
            # Knowledge graph
            Tool(
                name="query_knowledge",
                description="Query codebase knowledge graph",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                    },
                },
                handler=self._query_knowledge,
            ),
            # More tools...
        ]

    async def _analyze_code(self, code: str, language: str) -> Dict:
        """Analyze code handler."""
        from app.understanding.code_analyzer import CodeAnalyzer
        analyzer = CodeAnalyzer()
        return analyzer.analyze(code, language)

    async def start(self, host: str = "localhost", port: int = 3001):
        """Start MCP server."""
        await self.server.start(host, port)
```

### 2. MCP Client (`app/mcp/aitk_client.py`)

**Purpose**: Connect to AI Toolkit and other MCP servers

```python
from mcp import Client
from typing import List, Dict
import json

class AIToolkitMCPClient:
    """
    Client to connect to AI Toolkit MCP servers.
    """

    def __init__(self, config_path: str = "~/.aitk/mcp.json"):
        self.config = self._load_config(config_path)
        self.clients = {}
        self._connect_servers()

    def _load_config(self, path: str) -> Dict:
        """Load MCP server configuration."""
        with open(os.path.expanduser(path)) as f:
            return json.load(f)

    def _connect_servers(self):
        """Connect to all configured MCP servers."""
        for name, server_config in self.config["servers"].items():
            if server_config["type"] == "stdio":
                client = Client.stdio(
                    command=server_config["command"],
                    args=server_config["args"],
                )
            elif server_config["type"] == "http":
                client = Client.http(url=server_config["url"])

            self.clients[name] = client

    async def call_tool(
        self,
        server: str,
        tool: str,
        **kwargs
    ) -> Any:
        """Call tool on specific MCP server."""
        client = self.clients[server]
        return await client.call_tool(tool, **kwargs)

    async def list_tools(self, server: str) -> List[str]:
        """List available tools on server."""
        client = self.clients[server]
        return await client.list_tools()
```

### 3. Tool Registry (`app/mcp/tool_registry.py`)

**Purpose**: Centralized registry of all MCP tools

```python
from typing import Dict, List, Callable
from dataclasses import dataclass

@dataclass
class MCPTool:
    name: str
    description: str
    parameters: Dict
    handler: Callable
    category: str
    requires_auth: bool = False

class MCPToolRegistry:
    """
    Registry of all MCP tools.
    """

    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Register built-in tools."""

        # Code Analysis Tools
        self.register(MCPTool(
            name="analyze_code",
            description="Semantic code analysis",
            parameters={
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "language": {"type": "string"},
                },
            },
            handler=self._analyze_code,
            category="code_understanding",
        ))

        # Knowledge Graph Tools
        self.register(MCPTool(
            name="query_codebase",
            description="Query knowledge about codebase",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
            },
            handler=self._query_codebase,
            category="knowledge",
        ))

        # File Operations
        self.register(MCPTool(
            name="read_file_semantic",
            description="Read and understand file",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "include_context": {"type": "boolean"},
                },
            },
            handler=self._read_file_semantic,
            category="file_ops",
        ))

        # Reasoning Tools
        self.register(MCPTool(
            name="chain_of_thought",
            description="Perform chain-of-thought reasoning",
            parameters={
                "type": "object",
                "properties": {
                    "problem": {"type": "string"},
                    "steps": {"type": "integer"},
                },
            },
            handler=self._chain_of_thought,
            category="reasoning",
        ))

    def register(self, tool: MCPTool):
        """Register a new tool."""
        self.tools[tool.name] = tool

    def get(self, name: str) -> MCPTool:
        """Get tool by name."""
        return self.tools.get(name)

    def list_by_category(self, category: str) -> List[MCPTool]:
        """List tools by category."""
        return [t for t in self.tools.values() if t.category == category]
```

### 4. Local Model Integration (`app/mcp/local_models.py`)

**Purpose**: Integrate AI Toolkit local models

```python
import onnxruntime as ort
from pathlib import Path
from typing import Dict, Any

class LocalModelManager:
    """
    Manage local AI Toolkit models.
    """

    def __init__(self, aitk_path: str = "~/.aitk"):
        self.aitk_path = Path(aitk_path).expanduser()
        self.models = self._discover_models()
        self.sessions = {}

    def _discover_models(self) -> Dict[str, Path]:
        """Discover installed local models."""
        models = {}
        models_dir = self.aitk_path / "models"

        for model_dir in models_dir.glob("*/*/v*"):
            model_name = model_dir.parent.parent.name + "/" + model_dir.parent.name
            models[model_name] = model_dir

        return models

    def load_model(self, model_name: str):
        """Load local model for inference."""
        if model_name in self.sessions:
            return self.sessions[model_name]

        model_path = self.models[model_name]

        # Find ONNX model file
        onnx_files = list(model_path.glob("*.onnx"))
        if not onnx_files:
            raise ValueError(f"No ONNX model found in {model_path}")

        # Create ONNX Runtime session
        session = ort.InferenceSession(
            str(onnx_files[0]),
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        )

        self.sessions[model_name] = session
        return session

    async def infer(
        self,
        model_name: str,
        prompt: str,
        **kwargs
    ) -> str:
        """Run inference on local model."""
        session = self.load_model(model_name)

        # Tokenize and prepare input
        input_ids = self._tokenize(prompt, model_name)

        # Run inference
        outputs = session.run(None, {"input_ids": input_ids})

        # Decode output
        response = self._decode(outputs[0], model_name)

        return response
```

## MCP Tools to Implement

### Category 1: Code Understanding (15 tools)
- `analyze_code` - Semantic analysis
- `find_definitions` - Symbol lookup
- `trace_dependencies` - Dependency tracking
- `explain_code` - Natural language explanation
- `detect_patterns` - Design pattern recognition
- `calculate_metrics` - Code metrics
- `find_duplicates` - Code duplication detection
- `suggest_refactoring` - Refactoring suggestions
- `generate_tests` - Test generation
- `document_code` - Documentation generation
- `type_check` - Static type checking
- `lint_code` - Linting
- `format_code` - Code formatting
- `optimize_code` - Performance optimization
- `security_audit` - Security analysis

### Category 2: Knowledge Graph (10 tools)
- `query_knowledge` - Query knowledge graph
- `add_knowledge` - Add to knowledge graph
- `find_similar` - Semantic similarity search
- `get_context` - Retrieve context
- `trace_relations` - Relationship tracing
- `find_usage` - Usage tracking
- `get_dependencies` - Dependency graph
- `find_patterns` - Pattern discovery
- `suggest_related` - Related code suggestion
- `explain_architecture` - Architecture explanation

### Category 3: Reasoning (8 tools)
- `chain_of_thought` - CoT reasoning
- `plan_task` - Task planning
- `reflect` - Self-reflection
- `critique` - Code critique
- `compare_approaches` - Approach comparison
- `evaluate_complexity` - Complexity evaluation
- `suggest_alternatives` - Alternative suggestions
- `validate_logic` - Logic validation

### Category 4: File Operations (12 tools)
- `read_file_semantic` - Semantic file read
- `write_file_safe` - Safe file write
- `search_files` - Semantic file search
- `compare_files` - File comparison
- `merge_files` - Intelligent merge
- `extract_snippet` - Code snippet extraction
- `find_references` - Reference finding
- `rename_symbol` - Safe symbol renaming
- `move_code` - Code movement
- `split_file` - File splitting
- `organize_imports` - Import organization
- `remove_unused` - Unused code removal

### Category 5: Automation (10 tools)
- `run_task` - Execute automation task
- `check_status` - Task status
- `dry_run` - Preview actions
- `rollback` - Undo operations
- `schedule_task` - Task scheduling
- `monitor_execution` - Execution monitoring
- `get_logs` - Log retrieval
- `analyze_performance` - Performance analysis
- `generate_report` - Report generation
- `configure_automation` - Configuration

## Integration with AI Toolkit

### DeepSeek-R1 Local Model
```python
async def use_deepseek_local(prompt: str) -> str:
    """Use local DeepSeek-R1 for reasoning."""
    manager = LocalModelManager()
    return await manager.infer(
        "Microsoft/deepseek-r1-distill-qwen-14b",
        prompt,
        temperature=0.7,
        max_tokens=2048,
    )
```

### Qwen2.5-Coder Local Model
```python
async def use_qwen_coder_local(code_prompt: str) -> str:
    """Use local Qwen2.5-Coder for coding."""
    manager = LocalModelManager()
    return await manager.infer(
        "Microsoft/qwen2.5-coder-14b-instruct",
        code_prompt,
        temperature=0.3,
        max_tokens=4096,
    )
```

## Configuration

`config/mcp_config.yaml`:
```yaml
mcp:
  server:
    enabled: true
    host: localhost
    port: 3001
    max_connections: 100

  client:
    aitk_config: ~/.aitk/mcp.json
    servers:
      filesystem:
        enabled: true
      shell:
        enabled: true
        sandbox: true
      github:
        enabled: true
        requires_auth: true
      ollama:
        enabled: true
        url: http://127.0.0.1:11434

  local_models:
    enabled: true
    models_path: ~/.aitk/models
    preferred:
      reasoning: Microsoft/deepseek-r1-distill-qwen-14b
      coding: Microsoft/qwen2.5-coder-14b-instruct
```

## Implementation Timeline

### Week 1-2: Core MCP Infrastructure
- [ ] Implement MCP server
- [ ] Implement MCP client
- [ ] Create tool registry
- [ ] Add configuration system

### Week 3-4: Tool Implementation
- [ ] Implement 20 core tools
- [ ] Add error handling
- [ ] Create tool documentation
- [ ] Add tool tests

### Week 5-6: AI Toolkit Integration
- [ ] Connect to local models
- [ ] Integrate filesystem/shell servers
- [ ] Add GitHub MCP integration
- [ ] Performance optimization

### Week 7-8: Testing & Refinement
- [ ] Integration testing
- [ ] Performance testing
- [ ] Documentation
- [ ] Bug fixes

## Success Metrics

- **Tools**: 50+ MCP tools implemented
- **Performance**: <50ms tool execution overhead
- **Reliability**: 99.9% uptime
- **Coverage**: All major use cases supported
- **Compatibility**: Works with all MCP servers in config

## Next Steps

1. Set up MCP development environment
2. Implement core MCP server
3. Connect to AI Toolkit
4. Begin tool implementation
5. Create comprehensive tests
