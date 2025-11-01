# Glimpse Terminology Guide

## Core Components

### Glimpse
- **Term**: Glimpse
- **Description**: The core analysis and insight generation engine
- **Example**: `GlimpseEngine`, `GlimpseAnalyzer`

### Smart Vision (Deprecated)
- **New Term**: Glimpse Bridge
- **Old Term**: Smart Vision
- **Description**: The communication layer for Glimpse components
- **Example**: `GlimpseBridge` (was `SmartVisionBridge`)

## File Naming Conventions

### Configuration Files
- **Pattern**: `glimpse_*.yaml`
- **Example**: `glimpse_config.yaml`

### Core Modules
- **Pattern**: `glimpse_*.py`
- **Example**: `glimpse_analyzer.py`

## Code Conventions

### Class Naming
- **Core Classes**: `Glimpse*` (e.g., `GlimpseEngine`, `GlimpseBridge`)
- **Analysis Classes**: `Glimpse*Analyzer` (e.g., `GlimpseTrajectoryAnalyzer`)

### Method Naming
- **Core Methods**: `glimpse_*` for main operations
- **Analysis Methods**: `analyze_*` for analysis operations

## Documentation Standards

### Cross-References
- Use `Glimpse` when referring to the core technology
- Use `glimpse` (lowercase) for general references
- Use backticks for code references: `` `GlimpseEngine` ``

### Examples

**Correct**:
```python
from glimpse import GlimpseEngine
from glimpse.bridge import GlimpseBridge
```

## Common Patterns

### Log Messages
```python
logger.info("Glimpse analysis started")
logger.debug("Glimpse Bridge connected successfully")
```

### Error Messages
```python
raise GlimpseError("Analysis failed: insufficient data")
```

## Migration Notes

### From Smart Vision to Glimpse Bridge
1. Update imports:
   ```python
   # Old
   from glimpse import SmartVisionBridge
   
   # New
   from glimpse.bridge import GlimpseBridge
   ```

2. Update class names:
   ```python
   # Old
   bridge = SmartVisionBridge(config)
   
   # New
   bridge = GlimpseBridge(config)
   ```

## Best Practices

1. **Consistency**:
   - Use `Glimpse` (capital G) when referring to the technology
   - Use `glimpse` for general references
   - Be specific when referring to components (e.g., "Glimpse Engine", "Glimpse Bridge")

2. **Documentation**:
   - Include docstrings for all public APIs
   - Use type hints for better IDE support
   - Document any deprecated functionality

3. **Error Handling**:
   - Use specific exception types
   - Include meaningful error messages
   - Log errors with appropriate severity levels
