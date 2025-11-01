# Echoes Assistant V2 Core - Full Coverage Test Suite

## 🎯 Overview

This comprehensive test suite validates the complete functionality of `assistant_v2_core.py` through the Echoes API endpoints. It tests the OpenAI API migration between Chat Completions and Responses APIs, ensuring all features work correctly.

## 🧪 What Gets Tested

### **Core Migration Features**
- ✅ **Responses API Implementation**: Tool calling, streaming, message handling
- ✅ **Chat Completions Fallback**: Backward compatibility and error recovery
- ✅ **Dual API Support**: Seamless switching based on configuration
- ✅ **Streaming Responses**: Both APIs with proper chunk handling

### **Advanced Features**
- ✅ **Tool Calling Loop**: Multi-step tool execution with state management
- ✅ **Agent Actions**: Quantum state, inventory, ROI analysis
- ✅ **Workflow Orchestration**: Business initiative triage and execution
- ✅ **RAG Integration**: Knowledge search and retrieval
- ✅ **Error Handling**: Validation, API errors, fallbacks

### **Performance & Reliability**
- ✅ **Response Time Monitoring**: Latency tracking and optimization
- ✅ **Token Usage Tracking**: API cost monitoring
- ✅ **Error Resilience**: Circuit breaker patterns and recovery
- ✅ **Concurrent Load Testing**: Multi-worker execution

## 🚀 Quick Start

### **Option 1: Automated Setup (Windows)**
```batch
# Run the automated test setup
run_full_tests.bat
```

This will:
- Create/update virtual environment
- Install dependencies
- Start the API server
- Run all tests automatically
- Generate comprehensive reports

### **Option 2: Manual Setup**

1. **Start the API Server:**
```bash
# Terminal 1 - Start API server
uvicorn api.main:app --reload --port 8000
```

2. **Run Tests:**
```bash
# Terminal 2 - Run test suite
python full_coverage_test_runner.py --check-api --workers 4
```

## 📋 Test Categories

### **API Migration Tests (4 tests)**
- `responses_api_basic_chat` - Basic chat with Responses API
- `responses_api_streaming` - Streaming responses
- `responses_api_tool_calling` - Tool execution with Responses API
- `chat_completions_fallback` - Fallback to Chat Completions

### **Advanced Features (4 tests)**
- `responses_api_quantum_state` - Quantum state management
- `responses_api_workflow` - Business workflow orchestration
- `responses_api_knowledge_search` - RAG knowledge retrieval
- `responses_api_roi_analysis` - ROI calculation and analysis

### **Validation & Error Handling (4 tests)**
- `api_migration_validation` - Multi-turn conversations
- `error_handling_validation` - Input validation
- `performance_load_test` - Performance under load
- `fallback_to_chat_completions` - Error recovery mechanisms

## 📊 Output Files

The test suite generates multiple output formats:

- **`test_results_YYYYMMDD_HHMMSS.json`** - Complete test data with API responses
- **`performance_baseline.db`** - SQLite database for trend analysis
- **`test_suite.log`** - Detailed execution logs

## 🎮 Usage Examples

### **Basic Test Run**
```bash
python full_coverage_test_runner.py
```

### **Custom Configuration**
```bash
# Use custom test config
python full_coverage_test_runner.py --config my_tests.json

# Different API endpoint
python full_coverage_test_runner.py --api-url https://my-api.com

# Higher parallelism
python full_coverage_test_runner.py --workers 8
```

### **API Health Check**
```bash
# Check API before running tests
python full_coverage_test_runner.py --check-api
```

### **Performance Analysis**
```bash
# Analyze trends (requires historical data)
python full_coverage_test_runner.py --trend-analysis --days 7
```

## 🔧 Configuration

### **Test Configuration File** (`full_coverage_test_config.json`)

```json
{
  "tests": [
    {
      "name": "responses_api_basic_chat",
      "prompt": "Hello, how are you today?",
      "expected_outcome": "success",
      "timeout": 30,
      "tags": ["responses_api", "basic"],
      "metadata": {
        "use_responses_api": true,
        "model": "gpt-4o-mini"
      }
    }
  ],
  "settings": {
    "max_workers": 6,
    "test_categories": {
      "responses_api": ["responses_api_basic_chat"],
      "validation": ["error_handling_validation"]
    }
  }
}
```

### **Environment Variables**
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ECHOES_API_URL="http://localhost:8000"
```

## 📈 Test Results Interpretation

### **Success Metrics**
- **Response Time**: < 30s for basic queries, < 60s for complex analysis
- **Success Rate**: > 95% for properly configured tests
- **Token Efficiency**: Optimized usage across both APIs
- **Error Recovery**: Automatic fallback when primary API fails

### **Performance Trends**
```bash
# View performance trends
python full_coverage_test_runner.py --trend-analysis --days 30
```

Shows:
- Average response time improvements
- Success rate stability
- Token usage optimization
- API reliability metrics

## 🐛 Troubleshooting

### **API Server Issues**
```bash
# Check if server is running
curl http://localhost:8000/health

# View server logs
tail -f test_suite.log
```

### **Test Failures**
- Check `test_results_*.json` for detailed error messages
- Verify `OPENAI_API_KEY` is set correctly
- Ensure API endpoints are accessible
- Check firewall/proxy settings

### **Performance Issues**
- Reduce `--workers` if system resources are limited
- Increase `--timeout` for slower network connections
- Use `--mock` mode for offline testing

## 🏗️ Architecture

### **Test Runner Components**
```
full_coverage_test_runner.py
├── EchoesAPITester (main class)
│   ├── test_chat_completion()     # Basic chat tests
│   ├── test_agent_workflow()      # Workflow orchestration
│   ├── test_validation_error()    # Error handling
│   └── run_full_test_suite()      # Parallel execution
├── Test Configuration Loader
├── Results Aggregation
└── Performance Tracking
```

### **Integration Points**
- **API Endpoints**: `/api/ai/chat`, `/api/workflows/business-initiative`
- **Authentication**: Bearer token via `--api-key`
- **Configuration**: JSON-based test definitions
- **Parallelization**: ThreadPoolExecutor for concurrent testing

## 🎯 Coverage Areas

### **assistant_v2_core.py Features Tested**
- ✅ Dual API architecture (Responses vs Chat Completions)
- ✅ Tool calling loop with multi-step execution
- ✅ Streaming response handling
- ✅ Error recovery and fallback mechanisms
- ✅ Model selection and routing
- ✅ Context management and conversation history
- ✅ Value system integration
- ✅ RAG knowledge retrieval
- ✅ Agent action execution
- ✅ Workflow orchestration
- ✅ Performance metrics collection

### **Migration Validation**
- ✅ API parameter mapping (messages → input, etc.)
- ✅ Response format adaptation
- ✅ Tool call structure compatibility
- ✅ Streaming chunk processing
- ✅ Error handling consistency
- ✅ Performance parity

## 📚 Related Files

- `full_coverage_test_config.json` - Test configuration
- `full_coverage_test_runner.py` - Test execution Glimpse
- `run_full_tests.bat` - Windows automation script
- `assistant_v2_core.py` - System under test
- `api/main.py` - API server entry point
- `deployment_manager.py` - Deployment configuration

## 🤝 Contributing

To add new test cases:
1. Edit `full_coverage_test_config.json`
2. Add appropriate metadata for API selection
3. Implement test method in `EchoesAPITester` if needed
4. Update documentation

## 📄 License

This test suite is part of the Echoes Assistant V2 project.

---

**Ready to validate your OpenAI API migration? Run the tests now!** 🚀
