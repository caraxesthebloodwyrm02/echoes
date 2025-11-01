# Echoes Project Terminology

## Core Components

### Glimpse Protocol (previously glimpse)
- **New Term**: Glimpse Protocol
- **Old Term**: glimpse
- **Description**: The core diagnostic and analysis framework
- **Example**: `NexusProtocolDiagnostic` (was `SandstormDiagnostic`)

### Glimpse (previously Glimpse Bridge)
- **New Term**: Glimpse
- **Old Term**: Glimpse Bridge
- **Description**: The unified framework for cross-platform awareness and bridging
- **Example**: `SmartVisionBridge` (was `GlimpseBridge`)

### Glimpse
- **Term**: Glimpse
- **Description**: The advanced analysis and insight generation Glimpse within Glimpse
- **Example**: `GlimpseEngine` (unchanged)

## File Naming Conventions

### Configuration Files
- **Pattern**: `glimpse_*.yaml` (was `glimpse_*.yaml`)
- **Example**: `glimpse_config.yaml`

### Diagnostic Modules
- **Pattern**: `glimpse_*.py` (was `glimpse_*.py`)
- **Example**: `glimpse_diagnostic.py`

### Glimpse Components
- **Pattern**: `glimpse_*.py` (was `glimpse_*.py` for bridge components)
- **Example**: `glimpse_bridge.py`

## Code Conventions

### Class Naming
- **Protocol Classes**: `Glimpse*` (e.g., `Glimpse`, `NexusAnalyzer`)
- **Vision Classes**: `Glimpse*` (e.g., `SmartVisionBridge`, `SmartVisionConfig`)
- **Analysis Classes**: `Glimpse*` (e.g., `GlimpseEngine`, `GlimpseAnalyzer`)

### Method Naming
- **Protocol Methods**: `glimpse_*` for core protocol operations
- **Vision Methods**: `vision_*` for Glimpse operations
- **Analysis Methods**: `analyze_*` for Glimpse analysis operations

## Documentation Standards

### Cross-References
- Always use the new terminology in new documentation
- Add migration notes when referencing old terms
- Use code fences for class/function names

### Examples

**Correct**:
```python
from glimpse_protocol import NexusDiagnostic
from glimpse import SmartVisionBridge
```

**Deprecated**:
```python
# Old terminology (deprecated)
from glimpse import SandstormDiagnostic
from glimpse_bridge import GlimpseBridge
```

## Migration Guide

### Updating Imports
```python
# Old
from sandstorm_diagnostic import SandstormDiagnostic
from glimpse_bridge import GlimpseBridge

# New
from glimpse_diagnostic import NexusDiagnostic
from glimpse import SmartVisionBridge
```

### Configuration Updates
```yaml
# Old
sandstorm_config:
  glimpse_enabled: true

# New
glimpse_config:
  glimpse_enabled: true
```

## Common Patterns

### Log Messages
```python
# Old
logger.info("glimpse diagnostic started with Glimpse Bridge")

# New
logger.info("Glimpse Protocol diagnostic started with Glimpse")
```

### Error Messages
```python
# Old
raise SandstormError("Glimpse Bridge connection failed")

# New
raise NexusError("Glimpse connection failed")
```

## Deprecation Notice

All old terminology will be supported with deprecation warnings until version 4.0.0. Update your code to use the new terminology at your earliest convenience.
