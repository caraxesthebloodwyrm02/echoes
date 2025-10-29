# Glimpse Tools Test Suite

This directory contains comprehensive tests for the Glimpse integration tools in the Echoes Assistant V2.

## Overview

The Glimpse integration provides three main tools for enhanced API communication and cross-platform connectivity:

1. **GlimpseApiGetTool** - Enhanced GET requests with trajectory tracking and readability analysis
2. **GlimpseApiPostTool** - Enhanced POST requests with data flow analysis and connectivity assessment
3. **GlimpseConnectPlatformsTool** - Cross-platform integration for connecting different systems

## Test Files

### `test_glimpse_tools.py`
Full pytest test suite with 21 individual tests covering:
- Tool initialization and configuration
- Method availability (`get_stats`, `to_openai_schema`)
- Schema validation and JSON compatibility
- Statistics tracking and performance metrics
- Tool execution with mocked dependencies
- Integration testing across all tools

### `test_glimpse_tools_standalone.py`
Standalone test runner that can be executed directly without pytest:
- No external dependencies required
- Clear pass/fail reporting
- Can be run from any directory within the project
- Useful for quick validation during development

## Running the Tests

### Using pytest (Recommended)
```bash
# Run all Glimpse tests
cd /path/to/echoes
python -m pytest tests/glimpse/ -v

# Run specific test class
python -m pytest tests/glimpse/test_glimpse_tools.py::TestGlimpseApiGetTool -v

# Run specific test method
python -m pytest tests/glimpse/test_glimpse_tools.py::TestGlimpseApiPostTool::test_execute_method_with_json_data -v
```

### Using Standalone Runner
```bash
# Run from project root
cd /path/to/echoes
python tests/glimpse/test_glimpse_tools_standalone.py
```

## Test Coverage

The test suite covers:

✅ **Tool Initialization**
- Proper naming and descriptions
- Schema validation
- Required method availability

✅ **Statistics Tracking**
- `get_stats()` method functionality
- Call counting and error tracking
- Performance metrics (response times, operation times)

✅ **OpenAI Integration**
- `to_openai_schema()` method
- Valid JSON schema generation
- Function calling compatibility

✅ **Tool Execution**
- Mocked assistant interactions
- Different data types (JSON, form, raw string)
- Error handling and statistics updates

✅ **Registry Integration**
- Tool registration compatibility
- Method signature validation
- Statistics collection integration

## Expected Results

All tests should pass with output similar to:
```
============================= 21 passed in 0.06s =============================
```

Or for standalone runner:
```
📊 Test Results: 4/4 test suites passed
🎉 All tests passed! Glimpse integration is working correctly.
```

## Troubleshooting

### Import Errors
If you encounter module import errors, ensure you're running tests from the project root directory:
```bash
cd /path/to/echoes
```

### Missing Dependencies
The tests use standard library modules and `unittest.mock`. No additional dependencies are required beyond what's already in the project.

### Test Failures
If tests fail, check:
1. The `glimpse_tools.py` file is properly updated with `get_stats()` methods
2. Tool schemas match the expected structure
3. All required methods are implemented correctly

## Integration with CI/CD

These tests are automatically included in the project's pytest configuration and will run as part of the standard test suite.

## Related Files

- `tools/glimpse_tools.py` - Main implementation
- `glimpse_integration_example.py` - Usage examples
- `GLIMPSE_INTEGRATION_GUIDE.md` - User documentation
- `assistant_v2_core.py` - Tool registration
- `tools/registry.py` - Tool registry implementation
