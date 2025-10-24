# 📖 EchoesAssistantV2 - Complete Usage Guide

**Version**: 2.0
**Status**: ✅ Production Ready
**Last Updated**: October 22, 2025

---

## 🚀 Quick Start

```python
from assistant_v2_core import EchoesAssistantV2

# Initialize with all capabilities
assistant = EchoesAssistantV2(enable_tools=True)

# ✓ Knowledge management: Ready
# ✓ Filesystem tools: Ready
# ✓ Action execution: Ready
# ✓ Agent workflows: Ready
```

---

## 📋 Complete Feature Set

### 1. Knowledge Management

```python
# Gather knowledge
k_id = assistant.gather_knowledge(
    content="Your knowledge here",
    source="documentation.md",
    category="docs",
    tags=["important", "v2"]
)

# Search knowledge
results = assistant.search_knowledge(
    query="inventory",
    category="docs",
    limit=10
)

# Update context
assistant.update_context("current_task", "analysis")

# Get context summary
summary = assistant.get_context_summary()
```

### 2. Filesystem Operations

```python
# List directory
result = assistant.list_directory("ATLAS", pattern="*.py")

# Read file
result = assistant.read_file("ATLAS/README.md")

# Write file
result = assistant.write_file("output.txt", "content")

# Search files
result = assistant.search_files("test", search_path=".")

# Get directory tree
result = assistant.get_directory_tree("ATLAS", max_depth=3)
```

### 3. Action Execution

```python
# Inventory actions
result = assistant.execute_action(
    "inventory", "add_item",
    sku="SKU-001",
    name="Mouse",
    category="Peripherals",
    quantity=50,
    location="A1"
)

# Tool actions
result = assistant.execute_action(
    "tool", "calculator",
    expression="2+2"
)

# View action history
history = assistant.get_action_history(limit=10)

# Get action summary
summary = assistant.get_action_summary()
```

### 4. Multi-Agent Workflows

```python
# Data enrichment
result = assistant.run_workflow(
    workflow_type="data_enrichment",
    topic="What is ATLAS?",
    context={"source": "docs"}
)

# Planning helper
result = assistant.run_workflow(
    workflow_type="triage",
    user_input="Create a plan for new feature",
    context={"task_type": "planning"}
)

# Document comparison
result = assistant.run_workflow(
    workflow_type="comparison",
    file1="version1.py",
    file2="version2.py"
)
```

### 5. Conversational Interface

```python
# Simple chat
response = assistant.chat("What is ATLAS?")

# With system prompt
response = assistant.chat(
    message="Analyze the codebase",
    system_prompt="You are a code analyst"
)

# With streaming
response = assistant.chat(
    message="Tell me about inventory",
    stream=True
)
```

---

## 🎯 Use Case Examples

### Use Case 1: Project Analysis

```python
# Scan project
tree = assistant.get_directory_tree(".", max_depth=2)

# Read key files
for file in ["README.md", "setup.py", "requirements.txt"]:
    content = assistant.read_file(file)
    if content["success"]:
        assistant.gather_knowledge(
            content["content"],
            file,
            "project_docs"
        )

# Run enrichment workflow
result = assistant.run_workflow(
    workflow_type="data_enrichment",
    topic="Project structure and capabilities"
)

print(result["final_output"])
```

### Use Case 2: Document Workflow

```python
# Find all markdown files
docs = assistant.search_files("*.md")

# Compare two versions
result = assistant.run_workflow(
    workflow_type="comparison",
    file1="docs/v1/api.md",
    file2="docs/v2/api.md"
)

print("Changes:", result["final_output"])
```

### Use Case 3: Inventory Management

```python
# Add items
assistant.execute_action(
    "inventory", "add_item",
    sku="SKU-001",
    name="Laptop",
    category="Electronics",
    quantity=10,
    location="Store-A"
)

# Query natural language
result = assistant.run_workflow(
    workflow_type="triage",
    user_input="Show me all electronics with less than 5 items"
)

print(result["final_output"])
```

### Use Case 4: Code Analysis

```python
# Find Python files
py_files = assistant.search_files(".py")

# Analyze specific file
content = assistant.read_file("app/actions/action_executor.py")
assistant.gather_knowledge(
    content["content"],
    "action_executor.py",
    "code"
)

# Get explanation
result = assistant.run_workflow(
    workflow_type="triage",
    user_input="Explain how action_executor.py works"
)
```

### Use Case 5: Planning & Strategy

```python
# Create work plan
result = assistant.run_workflow(
    workflow_type="triage",
    user_input="""Create a plan for implementing user authentication:
    - Timeline: 2 weeks
    - Team size: 3 developers
    - Requirements: OAuth2, JWT, role-based access""",
    context={"task_type": "planning"}
)

print("Plan:", result["final_output"])
```

---

## 🔄 Workflow Patterns

### Pattern 1: Research & Synthesis

```python
# 1. Gather information
files = assistant.search_files("authentication")
for f in files["results"][:5]:
    content = assistant.read_file(f["path"])
    assistant.gather_knowledge(content["content"], f["path"], "auth")

# 2. Run enrichment workflow
result = assistant.run_workflow(
    workflow_type="data_enrichment",
    topic="Authentication implementation approach"
)

# 3. Store results
assistant.gather_knowledge(
    str(result["final_output"]),
    "workflow_result",
    "research"
)
```

### Pattern 2: Multi-Step Analysis

```python
# 1. Analyze structure
tree = assistant.get_directory_tree("app", max_depth=3)

# 2. Compare with expected
result = assistant.run_workflow(
    workflow_type="comparison",
    file1="app/current_structure.json",
    file2="app/expected_structure.json"
)

# 3. Generate plan
plan_result = assistant.run_workflow(
    workflow_type="triage",
    user_input="Create plan to align with expected structure",
    context={"differences": result["final_output"]}
)
```

### Pattern 3: Continuous Learning

```python
# 1. Execute actions and learn
result = assistant.execute_action("inventory", "list_items")

assistant.gather_knowledge(
    f"Inventory has {len(result['result'])} items",
    "inventory_scan",
    "data"
)

# 2. Answer questions using learned knowledge
response = assistant.chat(
    "How many inventory items do we have?"
)
```

---

## 🛠️ Configuration

### Assistant Initialization

```python
assistant = EchoesAssistantV2(
    model="gpt-4o",                    # OpenAI model
    temperature=0.7,                    # Response randomness
    max_tokens=4000,                    # Max response length
    rag_preset="balanced",              # RAG configuration
    enable_rag=True,                    # Enable RAG
    enable_tools=True,                  # Enable tools
    enable_streaming=True,              # Enable streaming
    enable_status=True,                 # Enable status indicators
    session_id="custom_session_123"    # Custom session ID
)
```

### Knowledge Manager

```python
# Custom storage path
from app.knowledge import KnowledgeManager
km = KnowledgeManager(storage_path="custom/path")
```

### Filesystem Tools

```python
# Custom root directory
from app.filesystem import FilesystemTools
fs = FilesystemTools(
    root_dir="/custom/root",
    allowed_patterns=["*.py", "*.md"]
)
```

---

## 📊 Statistics & Monitoring

```python
# Get comprehensive stats
stats = assistant.get_stats()

print(f"Session: {stats['session_id']}")
print(f"Messages: {stats['messages']}")
print(f"Knowledge entries: {stats['knowledge']['total_entries']}")
print(f"Actions executed: {stats['actions']['total_actions']}")
print(f"Success rate: {stats['actions']['success_rate']}%")

# Tool statistics
if 'tool_stats' in stats:
    print(f"Total tools: {stats['tool_stats']['total_tools']}")

# Action history
history = assistant.get_action_history(limit=10)
for action in history:
    print(f"{action['action_id']}: {action['action_type']} - {action['status']}")
```

---

## 🔒 Security & Safety

### Path Validation
- All filesystem operations validate paths
- Access limited to root directory
- Sensitive directories (.git, .env) blocked
- No access outside project

### Error Handling
- Graceful error recovery
- Detailed error messages
- No crashes or interruptions
- Safe defaults everywhere

### Resource Limits
- File size limits (1MB default)
- Search result limits (50 default)
- Directory depth limits (3 default)
- All configurable

---

## 🎓 Best Practices

### 1. Knowledge Management
```python
# ✓ Good: Specific categories
assistant.gather_knowledge(content, source, category="api_docs")

# ✗ Avoid: Generic categories
assistant.gather_knowledge(content, source, category="general")
```

### 2. Workflow Selection
```python
# ✓ Good: Use triage for auto-routing
result = assistant.run_workflow("triage", user_input=query)

# ✓ Good: Use specific workflow when known
result = assistant.run_workflow("comparison", file1=f1, file2=f2)
```

### 3. Context Building
```python
# ✓ Good: Update context as you work
assistant.update_context("current_file", "app.py")
assistant.update_context("files_processed", count)

# ✓ Good: Use context in workflows
result = assistant.run_workflow(
    "triage",
    user_input=query,
    context={"previous_results": results}
)
```

### 4. Error Handling
```python
# ✓ Good: Check success status
result = assistant.read_file("file.txt")
if result["success"]:
    process(result["content"])
else:
    log_error(result["error"])
```

---

## 🚨 Troubleshooting

### Issue: Workflow Timeout
```python
# Solution: Break into smaller steps
result1 = assistant.run_workflow("triage", user_input=part1)
result2 = assistant.run_workflow("triage", user_input=part2)
```

### Issue: Knowledge Not Found
```python
# Solution: Verify knowledge was added
stats = assistant.knowledge_manager.get_stats()
print(f"Total entries: {stats['total_entries']}")

# Add missing knowledge
assistant.gather_knowledge(content, source, category)
```

### Issue: File Access Denied
```python
# Solution: Check path is within root
import os
print(f"Root: {os.getcwd()}")
print(f"Target: {file_path}")

# Use relative paths from root
result = assistant.read_file("relative/path/file.txt")
```

---

## 📈 Performance Tips

### 1. Pre-load Common Knowledge
```python
# Load once at startup
common_docs = ["README.md", "API.md", "GUIDE.md"]
for doc in common_docs:
    content = assistant.read_file(doc)
    assistant.gather_knowledge(content["content"], doc, "docs")
```

### 2. Use Specific Queries
```python
# ✓ Fast: Specific query
result = assistant.search_knowledge(
    query="authentication implementation",
    category="code"
)

# ✗ Slow: Generic query
result = assistant.search_knowledge(query="code")
```

### 3. Limit Filesystem Scans
```python
# ✓ Fast: Targeted search
result = assistant.search_files("auth", search_path="app/auth")

# ✗ Slow: Full project scan
result = assistant.search_files("auth", search_path=".")
```

---

## 🎉 Summary

**EchoesAssistantV2 is a fully autonomous multi-agent system** with:

✅ **Knowledge Management** - Learn and remember
✅ **Filesystem Operations** - Navigate and analyze
✅ **Action Execution** - Execute tasks autonomously
✅ **Multi-Agent Workflows** - Complex multi-step operations
✅ **Conversational Interface** - Natural language interaction

**Ready for production use with zero crashes and full error handling.**

---

## 📞 Additional Resources

- `test_agentic_assistant.py` - Knowledge & filesystem tests
- `test_multi_agent_workflows.py` - Workflow tests
- `MULTI_AGENT_SYSTEM_COMPLETE.md` - Multi-agent documentation
- `AGENTIC_ASSISTANT_STREAMLINED.md` - Core capabilities
- `assistant_v2_core.py` - Source code

---

**Last Updated**: October 22, 2025, 9:03 AM
**Status**: ✅ **PRODUCTION READY**
