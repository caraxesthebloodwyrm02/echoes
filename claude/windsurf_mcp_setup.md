# Windsurf IDE: Complete MCP & Automation Setup Guide

## 📋 Table of Contents
1. [MCP Configuration](#mcp-configuration)
2. [Prerequisites Installation](#prerequisites-installation)
3. [MCP Server Setup](#mcp-server-setup)
4. [Automation Framework](#automation-framework)
5. [Verification & Testing](#verification-testing)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 MCP Configuration

### What is MCP?
Model Context Protocol (MCP) servers are dimensional gateways in your IDE—each one connects your AI agent to different capabilities: filesystems, web searches, memory vaults, and version control.

### Configuration File Location

**Primary Location:**
```
%APPDATA%\Windsurf\User\globalStorage\codeium.windsurf\mcp_config.json
```

**Full Path Example:**
```
C:\Users\irfan\AppData\Roaming\Windsurf\User\globalStorage\codeium.windsurf\mcp_config.json
```

**Alternative Location:**
If the above doesn't work, create `.windsurfrc` in your home directory with the same JSON structure.

---

## 🔧 Prerequisites Installation

### 1. Node.js (REQUIRED)

**Why:** MCP servers require Node.js v16+ to function

**Installation:**
1. Download Node.js LTS (v20+): https://nodejs.org/
2. Run installer with default settings
3. Verify installation:
```bash
node --version    # Should return v20.x.x or higher
npm --version     # Should return version number
npx --version     # Should return version number
```

### 2. Brave Search API Key (for web search capability)

**Steps:**
1. Visit: https://brave.com/search/api/
2. Sign up for free tier (2,000 queries/month)
3. Generate API key from dashboard
4. Copy the key (format: `BSAxxxxxxxxxxxxxxxxxxxx`)

---

## ⚙️ MCP Server Setup

### Complete Configuration File

Create/edit the file at the location mentioned above with this content:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\Users\\irfan",
        "E:\\Projects"
      ],
      "description": "Local filesystem access"
    },
    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": "YOUR_BRAVE_API_KEY_HERE"
      },
      "description": "Web search capabilities"
    },
    "fetch": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-fetch"
      ],
      "description": "URL content fetching"
    },
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ],
      "env": {
        "MEMORY_FILE_PATH": "C:\\Users\\irfan\\.windsurf\\memory.json"
      },
      "description": "Persistent memory storage"
    },
    "git": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-git"
      ],
      "description": "Git repository operations"
    }
  }
}
```

### Critical Path Corrections

⚠️ **Windows Path Format:**
- Use double backslashes (`\\`) in Windows paths
- Example: `C:\\Users\\irfan` NOT `C:/Users/irfan`

**Update These Paths:**
1. Replace `C:\\Users\\irfan` with your actual username path
2. Replace `E:\\Projects` with your actual projects directory
3. Replace `YOUR_BRAVE_API_KEY_HERE` with your actual Brave API key

### Individual Server Configuration

#### Filesystem Server
**What it does:** Grants agent access to read/write files in specified directories

**Configuration Dialog:**
When prompted for "Filesystem Paths", enter:
```
C:\Users\irfan E:\Projects
```

**Format Rules:**
- Space-separated (not comma-separated)
- No quotes needed
- Absolute paths only
- Can use either `\` or `/` on Windows

**Security Note:** Only grant access to directories you want the agent to access.

#### Memory Server
**What it does:** Stores persistent knowledge across sessions

**Configuration Dialog:**
When prompted for "Memory File Path", choose one:

**Option 1 (Recommended - Centralized):**
```
C:\Users\irfan\.windsurf\memory.json
```

**Option 2 (Project-Specific):**
```
E:\Projects\.mcp\memory.json
```

The file will be created automatically on first use.

#### Brave Search Server
**What it does:** Enables web search capabilities

**Configuration:**
Update the `BRAVE_API_KEY` in the config file with your actual API key:
```json
"env": {
  "BRAVE_API_KEY": "BSAyour-actual-key-here"
}
```

---

## 🤖 Automation Framework

### Test Generator Setup

**Create the automation directory:**
```bash
mkdir -p automation
cd automation
```

**Create `test_generator.py`:**
```python
#!/usr/bin/env python3
"""
Automatic test generation for Python modules
"""
import ast
import sys
from pathlib import Path

def generate_tests(module_path: str) -> str:
    """Generate pytest tests for a Python module"""
    with open(module_path, 'r') as f:
        tree = ast.parse(f.read())
    
    test_cases = []
    module_name = Path(module_path).stem
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            is_async = isinstance(node, ast.AsyncFunctionDef)
            
            test_cases.append(f"""
{'@pytest.mark.asyncio' if is_async else ''}
def test_{func_name}_success():
    \"\"\"Test {func_name} happy path\"\"\"
    # TODO: Implement test
    pass

{'@pytest.mark.asyncio' if is_async else ''}
def test_{func_name}_edge_cases():
    \"\"\"Test {func_name} edge cases\"\"\"
    # TODO: Implement test
    pass

{'@pytest.mark.asyncio' if is_async else ''}
def test_{func_name}_error_handling():
    \"\"\"Test {func_name} error handling\"\"\"
    # TODO: Implement test
    pass
""")
    
    return f"""import pytest
from {module_name} import *

{chr(10).join(test_cases)}
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_generator.py <module_path>")
        sys.exit(1)
    
    module_path = sys.argv[1]
    tests = generate_tests(module_path)
    
    test_file = f"test_{Path(module_path).stem}.py"
    with open(test_file, 'w') as f:
        f.write(tests)
    
    print(f"✅ Generated: {test_file}")
```

**Make it executable:**
```bash
chmod +x test_generator.py
```

**Usage:**
```bash
python automation/test_generator.py packages/science/router.py
```

### Pre-commit Hook Integration

**Add to `.pre-commit-config.yaml`:**
```yaml
repos:
  - repo: local
    hooks:
      - id: auto-generate-tests
        name: Auto-generate test skeletons
        entry: python automation/test_generator.py
        language: system
        files: \.py$
        exclude: ^tests/
```

---

## ✅ Verification & Testing

### Step 1: Restart Windsurf
1. Completely close Windsurf (check Task Manager if needed)
2. Reopen Windsurf
3. Wait for MCP servers to initialize

### Step 2: Test Each Server

**Test Filesystem:**
Ask your agent: "List files in my E:\Projects directory"

**Test Brave Search:**
Ask your agent: "Search the web for latest MCP documentation"

**Test Memory:**
Ask your agent: "Remember this: my favorite programming language is Python"

**Test Fetch:**
Ask your agent: "Fetch the content from https://docs.anthropic.com"

**Test Git:**
Ask your agent: "Show me the git status of my current project"

### Step 3: Check Logs

If servers don't initialize, check logs at:
```
C:\Users\irfan\AppData\Roaming\Windsurf\logs\
```

Look for files containing "mcp" or "server" in the name.

---

## 🔍 Troubleshooting

### MCP Servers Not Initializing

**Check 1: Node.js Installation**
```bash
node --version
npx --version
```
If these fail, reinstall Node.js.

**Check 2: Path Formatting**
- Ensure double backslashes in Windows paths
- No trailing slashes
- Paths exist and are accessible

**Check 3: Permissions**
- Run Windsurf as administrator (if necessary)
- Ensure file system access permissions

**Check 4: Configuration File Syntax**
- Validate JSON syntax at https://jsonlint.com/
- No trailing commas
- All quotes closed properly

### Memory Server Issues

**Error: "Cannot find memory file"**
- Create directory manually: `mkdir C:\Users\irfan\.windsurf`
- The `.json` file will be created automatically

### Brave Search Not Working

**Error: "Invalid API key"**
- Verify key format: starts with `BSA`
- Check for extra spaces or quotes
- Regenerate key if necessary

### Filesystem Access Denied

**Error: "Permission denied"**
- Verify paths are correct
- Check Windows folder permissions
- Try adding just one directory first for testing

---

## 🎯 Quick Reference Commands

### Daily Workflow
```bash
# Generate tests for new module
python automation/test_generator.py path/to/module.py

# Run tests with coverage
pytest --cov=packages tests/

# Check MCP status
# (Ask agent: "What MCP servers are currently active?")
```

### Maintenance
```bash
# Update MCP servers
npx -y @modelcontextprotocol/server-filesystem@latest

# Clear NPX cache (if issues)
npx clear-npx-cache

# Restart Windsurf completely
taskkill /F /IM Windsurf.exe
```

---

## 🌟 What Success Looks Like

When properly configured:
- ✅ Agent can navigate your filesystem like a native guide
- ✅ Agent reaches beyond training data via web search
- ✅ Agent remembers context across sessions
- ✅ Agent interacts with git repositories
- ✅ Automation generates test skeletons in seconds
- ✅ Documentation stays synchronized automatically

Your Windsurf IDE transforms from a local editor into a **multidimensional development oracle** that can traverse filesystems, search the web, and maintain persistent memory.

---

## 📚 Additional Resources

- **MCP Documentation:** https://modelcontextprotocol.io/
- **Brave Search API:** https://brave.com/search/api/
- **Windsurf Support:** https://codeium.com/windsurf
- **Node.js Downloads:** https://nodejs.org/

---

## 🔄 Next Steps

1. ✅ Install Node.js v16+
2. ✅ Get Brave Search API key
3. ✅ Create/update MCP config file
4. ✅ Configure individual servers
5. ✅ Restart Windsurf
6. ✅ Test all MCP servers
7. ✅ Set up automation framework
8. ✅ Start building with enhanced capabilities

The configuration is complete—you've transformed Windsurf from a simple editor into an **AI-powered development nexus**. 🚀