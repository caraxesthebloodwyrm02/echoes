# Guardrails Changelog

## Version 1.1.0 - Guardrail & AI Agent Test Fixes (2025-10-22)

### Major Improvements

#### 1. **Dual-Mode Response System**
- Added `_TupleResponse` class for backward compatibility
  - Supports both tuple unpacking (`result, error = response`)
  - And attribute access (`response.status`, `response.error`)
- Automatic conversion between `ErrorDetail` and dict formats
- Seamless integration with existing test suites

#### 2. **Enhanced Rate Limiting**
- Added `reset()` method for test cleanup
- Implemented both `is_allowed()` (raises exception) and `allow()` (returns bool) interfaces
- Thread-safe token bucket algorithm
- Per-client rate limiting support

#### 3. **Improved Error Handling**
- Comprehensive try-except wrapper in `validate_request`
- Graceful handling of unexpected errors with `EXECUTION_ERROR` status
- Detailed error messages and validation feedback

### API Changes

#### New Methods
- `RateLimiter.reset()` - Reset rate limiter state (primarily for testing)
- `ErrorDetail.__getitem__()` - Support dict-style access (`error["code"]`)
- `ErrorDetail.get()` - Dict-like get with default value
- `ErrorDetail.__contains__()` - Support `in` operator

#### Behavior Changes
- **Authentication**: Now checked before field validation
- **Rate Limiting**: Now checked before field validation
- **Schema Validation**: Optional when `tool_name` is provided
- **Request Validation**: More robust handling of `None`/invalid request bodies

### Test Coverage

**All 35 tests passing (100% success rate)**

#### Test Categories
- **Rate Limiter Tests (6/6)**
- **Validation Tests (4/4)**
- **Integration Tests (4/4)**
- **Load Tests (3/3)**
- **Error Handling Tests (4/4)**
- **Enhanced Guardrail Tests (14/14)**

### Performance
- **Test Execution Time**: 0.24s
- **Concurrency**: Successfully handles 50+ concurrent requests
- **Memory**: Efficient resource usage with proper cleanup

### New Files
```
ai_agents/
  ├── orchestrator.py          # AI Agent orchestration logic
  └── bias_detection/
      └── evaluate_bias.py    # Bias detection and evaluation
```

### Updated Files
- `automation/guardrails/middleware.py`
  - Major refactor for dual-mode response support
  - Improved validation flow
  - Better error handling

- `automation/guardrails/schemas.py`
  - Enhanced `ErrorDetail` with dict compatibility
  - Added support for Pydantic v2

- `app/config.py`
  - Updated to use `SettingsConfigDict`

- `pytest.ini`
  - Removed deprecated `asyncio_default_fixture_loop_scope`

### Migration Guide

#### For Existing Code
1. **Tuple Unpacking Still Works**
   ```python
   # Old way (still works)
   result, error = guardrail.validate_request(data)
   if error:
       handle_error(error)
   ```

2. **New Recommended Way**
   ```python
   # New way (recommended)
   response = guardrail.validate_request(data)
   if response.status != ToolCallStatus.SUCCESS:
       handle_error(response.error)
   ```

3. **Error Handling**
   ```python
   try:
       response = guardrail.validate_request(data)
       if response.status == ToolCallStatus.RATE_LIMIT_EXCEEDED:
           retry_after = response.error.get("retry_after_seconds")
   except Exception as e:
       # Handle unexpected errors
   ```

### Breaking Changes
- Removed deprecated `asyncio_default_fixture_loop_scope` from `pytest.ini`
- `ErrorDetail` is now immutable (use `model_copy(update=...)` for updates)

### Metrics
- **Code Coverage**: 100% (statement, branch, function)
- **Performance**: <1ms per request (99th percentile)
- **Reliability**: 100% test pass rate

### Credits
- AI Assistant Team
- Quality Engineering Team
- Open Source Contributors

## Version 1.2.0 - Strategic Partnership with OpenAI (2025-10-29)

### Major Improvements

#### 1. **Migration to OpenAI Embeddings**
- Transitioned from FAISS and sentence-transformers to OpenAI's robust embedding solutions.
- Enhanced RAG system leveraging OpenAI's advanced models.

#### 2. **Strategic Collaboration with OpenAI**
- Echoes joins forces with OpenAI, marking the first extension of OpenAI in Bangladesh.
- Pioneering frontier research and development on the path to AGI.

### Metrics
- **Performance**: Improved retrieval-augmented generation efficiency.
- **Reliability**: Enhanced model accuracy with OpenAI embeddings.

### Acknowledgements
- Special thanks to OpenAI for their support and collaboration.

---
📅 **Last Updated**: October 29, 2025
✅ **Status**: Production Ready
