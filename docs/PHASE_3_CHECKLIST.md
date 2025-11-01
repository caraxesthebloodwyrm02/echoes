# Phase 3: MCP Integration - Implementation Checklist

## Overview
**Duration**: 4-6 weeks
**Priority**: HIGH
**Status**: 📋 Ready to Start
**Goal**: Enable standardized tool calling and resource access via Model Context Protocol

---

## Week 1-2: MCP Client Foundation

### Task 1.1: MCP Client Core
- [ ] Create `app/core/mcp/` directory
- [ ] Create `app/core/mcp/mcp_client.py`
  - [ ] MCPClient class
  - [ ] Server connection management
  - [ ] WebSocket communication
  - [ ] JSON-RPC handling
- [ ] Create `app/core/mcp/__init__.py`
- [ ] Glimpse tests: `tests/test_mcp_client.py`

**Success Criteria**: Connect to AI Toolkit filesystem server

### Task 1.2: Configuration
- [ ] Update `automation/config/lumina_config.yaml`
  - [ ] Add MCP server configurations
  - [ ] Enable/disable flags
  - [ ] Server paths
- [ ] Load MCP config in `app/core/lumina.py`
- [ ] Validate configuration on startup

### Task 1.3: Basic Tools
- [ ] Implement `call_tool()` method
- [ ] Implement `list_tools()` method
- [ ] Test with filesystem server
  - [ ] Read file
  - [ ] List directory
  - [ ] Write file
- [ ] Error handling and retry logic

**Deliverable**: Working MCP client that can call filesystem tools

---

## Week 2-3: Tool Registry & Management

### Task 2.1: Tool Registry
- [ ] Create `app/core/mcp/tool_registry.py`
  - [ ] ToolRegistry class
  - [ ] Tool registration
  - [ ] Tool discovery
  - [ ] Tool metadata
- [ ] Define `MCPTool` interface
- [ ] Auto-discover tools from servers

### Task 2.2: Resource Management
- [ ] Implement `list_resources()` method
- [ ] Implement `read_resource()` method
- [ ] Resource caching
- [ ] Resource expiration

### Task 2.3: Integration with Executor
- [ ] Update `autonomous_executor.py`
  - [ ] Add MCP client initialization
  - [ ] Use MCP for file operations
  - [ ] Tool calling in execution phases
- [ ] Replace direct file access with MCP calls
- [ ] Performance comparison (before/after)

**Deliverable**: Tool registry with auto-discovery and executor integration

---

## Week 3-4: Advanced MCP Features

### Task 3.1: GitHub MCP Server
- [ ] Connect to GitHub MCP server
- [ ] Implement repository operations
  - [ ] List repositories
  - [ ] Read files from GitHub
  - [ ] Create issues
  - [ ] Pull requests
- [ ] Test with actual GitHub account

### Task 3.2: Shell MCP Server
- [ ] Connect to shell server
- [ ] Implement command execution
- [ ] Security sandboxing
- [ ] Output streaming
- [ ] Test with safe commands

### Task 3.3: Ollama MCP Server
- [ ] Connect to Ollama server
- [ ] List available models
- [ ] Execute local model inference
- [ ] Compare with GitHub Models
- [ ] Performance benchmarks

**Deliverable**: Integration with 3+ MCP servers

---

## Week 4-5: MCP Tools Implementation

### Task 4.1: Code Understanding Tools
- [ ] Create `app/core/mcp/tools/code_understanding.py`
  - [ ] AST parsing tool
  - [ ] Symbol search tool
  - [ ] Dependency analysis tool
  - [ ] Code metrics tool
- [ ] Integration with knowledge graph (prep for Phase 4)

### Task 4.2: File Operation Tools
- [ ] Create `app/core/mcp/tools/file_operations.py`
  - [ ] Smart file search
  - [ ] Batch file operations
  - [ ] Safe file refactoring
  - [ ] Backup/restore
- [ ] Safety checks and validations

### Task 4.3: Reasoning Tools
- [ ] Create `app/core/mcp/tools/reasoning_tools.py`
  - [ ] Chain-of-thought helper
  - [ ] Self-reflection tool
  - [ ] Planning tool
  - [ ] Validation tool
- [ ] Integration with stick shift controller

**Deliverable**: 10+ custom MCP tools

---

## Week 5-6: Testing & Optimization

### Task 5.1: Integration Testing
- [ ] Create `tests/integration/test_mcp_full.py`
- [ ] End-to-end workflow tests
  - [ ] Natural language → MCP tool execution
  - [ ] Multi-server coordination
  - [ ] Error recovery
- [ ] Load testing (concurrent requests)

### Task 5.2: Performance Optimization
- [ ] Profile MCP calls
- [ ] Implement caching
  - [ ] Tool result caching
  - [ ] Resource caching
  - [ ] Connection pooling
- [ ] Async optimization
- [ ] Target: <100ms overhead per tool call

### Task 5.3: Documentation
- [ ] Create `docs/MCP_INTEGRATION_GUIDE.md`
- [ ] API documentation
- [ ] Usage examples
- [ ] Troubleshooting guide
- [ ] Update `MASTER_DEVELOPMENT_PLAN.md`

### Task 5.4: Demo & Examples
- [ ] Create `examples/mcp_demo.py`
  - [ ] Connect to servers
  - [ ] Execute tools
  - [ ] Show resources
  - [ ] Interactive mode
- [ ] Update `use_lumina.py` to showcase MCP

**Deliverable**: Production-ready MCP integration with full documentation

---

## Dependencies to Install

```bash
# MCP SDK
pip install mcp-sdk

# Additional dependencies
pip install websockets aiohttp

# For code understanding tools
pip install tree-sitter tree-sitter-python

# For testing
pip install pytest-asyncio pytest-mock
```

---

## Configuration Example

```yaml
# automation/config/lumina_config.yaml
lumina:
  mcp:
    enabled: true
    servers:
      - name: filesystem
        type: stdio
        command: node
        args: ["~/.aitk/mcp-servers/filesystem/index.js"]

      - name: github
        type: stdio
        command: node
        args: ["~/.aitk/mcp-servers/github/index.js"]
        env:
          GITHUB_TOKEN: "${GITHUB_TOKEN}"

      - name: ollama
        type: http
        url: "http://localhost:11434"

    tools:
      cache_enabled: true
      cache_ttl: 300
      timeout: 30
      retry_count: 3
```

---

## Success Metrics

### Functionality
- [ ] Connect to 5+ MCP servers
- [ ] Execute 20+ different tools
- [ ] Tool success rate >95%
- [ ] Resource access working

### Performance
- [ ] Tool call overhead <100ms
- [ ] Concurrent requests: 10+
- [ ] Cache hit rate >60%
- [ ] No memory leaks

### Quality
- [ ] Integration tests pass 100%
- [ ] Glimpse test coverage >80%
- [ ] No critical bugs
- [ ] Documentation complete

---

## Risk Mitigation

### Risk 1: MCP Server Availability
**Mitigation**: Implement fallback to direct API calls
```python
async def call_tool_with_fallback(tool_name, args):
    try:
        return await mcp_client.call_tool(tool_name, args)
    except MCPError:
        return await direct_api_call(tool_name, args)
```

### Risk 2: Performance Degradation
**Mitigation**: Aggressive caching and async execution
```python
@lru_cache(maxsize=1000)
async def cached_tool_call(tool_name, args_hash):
    return await mcp_client.call_tool(tool_name, args)
```

### Risk 3: Complex Tool Discovery
**Mitigation**: Manual tool registration as fallback
```python
# Auto-discovery + manual registration
registry.auto_discover()
registry.register_tool(custom_tool)  # Manual override
```

---

## Daily Standup Questions

1. **What did you complete yesterday?**
2. **What will you work on today?**
3. **Any blockers?**

### Week 1 Focus
- MCP client connection
- Basic tool execution
- Filesystem server integration

### Week 2 Focus
- Tool registry
- Multiple server support
- Executor integration

### Week 3 Focus
- GitHub integration
- Shell integration
- Ollama integration

### Week 4 Focus
- Custom tools
- Code understanding
- File operations

### Week 5 Focus
- Testing
- Optimization
- Documentation

### Week 6 Focus
- Polish
- Demo
- Launch prep

---

## Code Templates

### MCP Client Template
```python
# app/core/mcp/mcp_client.py
class MCPClient:
    def __init__(self, server_configs: List[Dict]):
        self.servers = {}
        self.tools = {}

    async def connect(self, server_config: Dict):
        """Connect to MCP server."""
        pass

    async def call_tool(self, tool_name: str, args: Dict) -> Any:
        """Call MCP tool."""
        pass

    async def list_resources(self, server: str) -> List[Resource]:
        """List available resources."""
        pass
```

### Tool Registry Template
```python
# app/core/mcp/tool_registry.py
class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register_tool(self, tool: MCPTool):
        """Register tool."""
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> MCPTool:
        """Get tool by name."""
        return self.tools.get(name)
```

---

## Phase 3 Completion Criteria

✅ **All tasks completed**
✅ **Tests passing (100%)**
✅ **Documentation complete**
✅ **Demo working**
✅ **Performance targets met**
✅ **Integration with natural language executor**
✅ **Ready for Phase 4 (Knowledge Graph)**

---

**Start Date**: TBD
**Target Completion**: 6 weeks from start
**Owner**: Development Team
**Stakeholders**: Lumina Users

**Let's build Phase 3!** 🚀
