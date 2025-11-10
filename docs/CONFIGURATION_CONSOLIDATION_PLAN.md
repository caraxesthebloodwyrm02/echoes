# Configuration Consolidation Plan

**Date**: November 2, 2025  
**Priority**: HIGH  
**Issue**: 6 configuration files using different systems

## Current Configuration Files

1. **`api/config.py`** - API server config (BaseSettings)
   - SelectiveAttentionConfig
   - EngineConfig  
   - SecurityConfig
   - APIConfig
   - EchoesAPIConfig (main)

2. **`echoes/config.py`** - Core Echoes config (dataclass)
   - RuntimeOptions
   - DEFAULT_MODEL, DEFAULT_TEMPERATURE, etc.

3. **`ATLAS/echoes/config.py`** - ATLAS-specific (BaseSettings)
   - Settings class with many fields

4. **`misc/Accounting/core/config.py`** - Accounting module
5. **`misc/Accounting/openai_prototype/config.py`** - Prototype
6. **Module-specific configs** - Various locations

## Analysis

### Usage Patterns

**api/config.py**:
- Used by API server
- Full BaseSettings with environment variable support
- Comprehensive configuration

**echoes/config.py**:
- Used by EchoesAssistantV2 core
- Simple dataclass (RuntimeOptions)
- Feature flags and runtime options

**ATLAS/echoes/config.py**:
- ATLAS-specific settings
- Database, server, security configs

## Recommended Approach

### Option 1: Keep Separate But Standardize (RECOMMENDED)

**Rationale**: Each config serves different purposes:
- `api/config.py` - API server needs
- `echoes/config.py` - Core assistant runtime options
- `ATLAS/echoes/config.py` - ATLAS module needs

**Action**: Standardize all to use `pydantic-settings BaseSettings`

### Option 2: Unified Configuration

**Approach**: Create single `echoes/core/config.py` with all configs
- Pros: Single source of truth
- Cons: Tight coupling, harder to maintain

**Not Recommended** due to different use cases

## Implementation Plan

### Phase 1: Standardize to BaseSettings

1. **Convert `echoes/config.py`**:
   - Convert RuntimeOptions dataclass to BaseSettings
   - Keep same structure, add env var support
   - Maintain backward compatibility

2. **Review and align**:
   - Ensure consistent naming
   - Document all environment variables
   - Create .env.example with all variables

### Phase 2: Documentation

1. **Create configuration guide**:
   - Document all config options
   - List all environment variables
   - Provide examples

2. **Environment variable mapping**:
   - Map each config option to env var
   - Document required vs optional

### Phase 3: Validation

1. **Startup validation**:
   - Validate all required configs
   - Clear error messages
   - Health check endpoint

## Priority Actions

1. ⏳ Convert `echoes/config.py` to BaseSettings (maintain compatibility)
2. ⏳ Create comprehensive .env.example
3. ⏳ Document all environment variables
4. ⏳ Add config validation on startup

**Status**: Plan ready - awaiting decision on approach

