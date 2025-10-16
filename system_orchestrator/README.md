# System Orchestrator

**Enterprise-grade Windows 11 + Windsurf + Python system orchestration environment**

## Overview

Comprehensive system-level orchestration platform with:
- ✅ Dependency injection container
- ✅ Windows Registry/COM/DLL integration
- ✅ Background system monitoring (CPU, memory, disk, network)
- ✅ HTTP client with async support
- ✅ OpenAI integration for intelligent orchestration
- ✅ Encryption and credential management
- ✅ Process management and system control
- ✅ Rich console output and structured logging
- ✅ PyInstaller deployment support

---

## Quick Start

```bash
# Install dependencies
pip install -r system_orchestrator/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with OPENAI_API_KEY

# Run orchestrator
python -m system_orchestrator
```

---

## Architecture

```
system_orchestrator/
├── core/
│   ├── bootstrap.py          # System initialization & lifecycle
│   ├── config.py             # Configuration (.env, YAML)
│   └── container.py          # Dependency injection
├── platform/
│   └── windows_integration.py # Registry, COM, DLL
├── monitoring/
│   └── system_monitor.py     # Background monitoring
├── networking/
│   └── http_client.py        # HTTP/OpenAI
├── security/
│   └── encryption.py         # Encryption/credentials
└── deploy/
    └── build_windows.spec    # PyInstaller config
```

---

## Features

### Configuration Management
- **Sources:** `.env` and `config.yaml`
- **Validation:** Pydantic `extra="forbid"`
- **Paths:** Cross-platform `pathlib.Path`

### Dependency Injection
- **Patterns:** Singleton, transient, factory
- **Resolution:** Automatic constructor injection
- **Context:** Request-scoped services

### Windows Integration
- **Registry:** `winreg` read/write
- **COM:** `win32com.client` integration
- **DLL:** `ctypes.windll` system calls
- **Credentials:** Windows Credential Manager

### System Monitoring
- **Metrics:** CPU, memory, disk, network
- **Background:** Thread-safe monitoring
- **Processes:** tasklist, taskkill, netstat

### Networking
- **HTTP:** `httpx` with retry logic
- **Async:** `asyncio` support
- **OpenAI:** Intelligent orchestration

### Security
- **Encryption:** Fernet symmetric encryption
- **Keyring:** System or encrypted fallback
- **Auth:** `getpass` interactive prompts

---

## Usage Examples

### Basic Orchestrator
```python
from system_orchestrator import SystemOrchestrator

orchestrator = SystemOrchestrator()
orchestrator.bootstrap()
orchestrator.verify_environment()
diagnostics = orchestrator.get_diagnostics()
orchestrator.shutdown()
```

### System Monitoring
```python
from system_orchestrator.monitoring.system_monitor import SystemMonitor

monitor = SystemMonitor(interval_seconds=60)
monitor.start()

metrics = monitor.get_latest_metrics()
print(f"CPU: {metrics.cpu_percent}%")

processes = monitor.list_processes(filter_name="python")
monitor.stop()
```

### Windows Integration
```python
from system_orchestrator.platform.windows_integration import (
    WindowsRegistry, WindowsDLL, WindowsCredentialManager
)

# Registry
registry = WindowsRegistry()
value = registry.read_value(r"Software\Microsoft\Windows\CurrentVersion", "ProgramFilesDir")

# DLL
dll = WindowsDLL()
is_admin = dll.is_admin()

# Credentials
cred_mgr = WindowsCredentialManager()
cred_mgr.store_credential("MyApp", "user", "password")
```

---

## Configuration

### `.env`
```bash
OPENAI_API_KEY=sk-proj-your-key
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### `config.yaml`
```yaml
monitoring:
  enabled: true
  interval_seconds: 60

security:
  encryption_enabled: true
  use_system_keyring: true
```

---

## Deployment

```bash
# Build executable
pyinstaller system_orchestrator/deploy/build_windows.spec

# Output: dist/SystemOrchestrator.exe
```

---

## Health Checks

| Check | Status |
|-------|--------|
| Configuration | ✓ |
| Logging | ✓ |
| Container | ✓ |
| Monitoring | ✓ |
| HTTP Client | ✓ |
| Platform | ✓ |

---

## License

MIT License - Copyright (c) 2025 Echoes Project
