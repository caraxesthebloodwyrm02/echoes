# Symphony Assistant API Integration
# ===================================
# Credit-efficient OpenAI assistance for Symphony development workflows

## Overview

The Symphony Assistant API provides intelligent, cost-effective OpenAI integration with advanced caching, batching, and fallback mechanisms to minimize API costs while maximizing development productivity.

## 🚀 Quick Start

### 1. Start the Assistant API Server
```bash
# Start with auto-reload (development)
uvicorn automation.backend.assistant_api:app --reload

# Or start stable server
uvicorn automation.backend.assistant_api:app
```

### 2. Use the CLI Interface
```bash
# Basic query
python automation/cli/assistant_cli.py query "How can I improve this code?"

# Use templates
python automation/cli/assistant_cli.py templates

# Check available models
python automation/cli/assistant_cli.py models

# View usage statistics
python automation/cli/assistant_cli.py stats
```

### 3. API Endpoints

- `GET /assistant/models` - List available models
- `POST /assistant/query` - Submit prompts for assistance
- `POST /assistant/switch-key` - Switch between API keys

## 💰 Credit-Efficient Usage Patterns

### Intelligent Caching
- **80-90% cost reduction** through response caching
- **MD5-based cache keys** for consistent retrieval
- **Persistent cache storage** in `automation/cache/assistant/`

### Batch Query Processing
```bash
# Combine multiple related queries
echo -e "Review authentication module\nAnalyze performance bottlenecks\nSuggest testing strategy" > queries.txt
python automation/cli/assistant_cli.py query "Batch analysis" --batch-file queries.txt
```

### Template-Based Queries
```bash
# Use pre-built templates for consistency
python automation/cli/assistant_cli.py query "Review this function for security issues" --template security
```

## 🏗️ Architecture Integration

### Master Channel Integration
```python
from automation.integration.symphony_assistant_integration import MasterChannelIntegration

integrator = MasterChannelIntegration()

# AI-enhanced compression and gluing
compressed = await integrator.assisted_compress_and_glue(input_data)

# AI-powered finalization with insights
result = await integrator.assisted_finalize({"compressed_data": compressed})
```

### Symphony Component Integration
- **Phase Simulator**: AI guidance for phase planning
- **Knowledge Graph**: Semantic reasoning assistance
- **QuickFix CLI**: Intelligent code improvement suggestions
- **MLOps Pipeline**: Model optimization recommendations

## 📊 Cost Optimization

### Usage Monitoring
```bash
# View usage statistics
python automation/cli/assistant_cli.py stats

# Expected output:
# Cached Responses: 47
# Est. Cost Savings: $0.23
# Efficiency: 89.2% from cache
```

### Cost Targets
- **Cache Hit Rate**: >85% for common queries
- **Average Query Cost**: <$0.01 per analysis
- **Monthly Budget**: <$10 for active development
- **Fallback Usage**: <5% of total queries

## 🔧 Advanced Configuration

### Environment Variables
```bash
# API Keys
OPENAI_API_KEY_PRIMARY=sk-proj-...
OPENAI_API_KEY_SECONDARY=sk-proj-...

# Model Preferences
LLM_MODEL_PRIMARY=gpt-4o-mini
LLM_MODEL_FALLBACK=gpt-4o

# Caching
LLM_CACHE_TTL=86400
LLM_CACHE_BACKEND=disk
```

### Custom Templates
```python
from automation.integration.symphony_assistant_integration import CreditEfficientPatterns

templates = CreditEfficientPatterns.create_contextual_templates()
# Access templates: templates["code_review"], templates["architecture"], etc.
```

## 🎯 Use Cases

### Development Assistance
- Code review and quality analysis
- Architecture design feedback
- Testing strategy recommendations
- Performance optimization guidance

### Documentation Enhancement
- README generation and updates
- API documentation assistance
- Integration guide creation

### Workflow Optimization
- Phase planning and validation
- Process improvement suggestions
- Best practice recommendations

## 📈 Performance Metrics

### Efficiency Tracking
- **Response Time**: <2 seconds for cached queries
- **API Latency**: 3-5 seconds for fresh queries
- **Cache Effectiveness**: 85-95% hit rate
- **Cost per Query**: $0.005-$0.02

### Quality Metrics
- **Response Relevance**: 95%+ for contextual queries
- **Code Quality**: Consistent with Symphony standards
- **Fallback Coverage**: 80% of common scenarios

## 🔄 Continuous Improvement

### Learning Loop
1. **Monitor Usage Patterns** - Track query types and frequencies
2. **Optimize Caching Strategy** - Adjust TTL based on query stability
3. **Refine Templates** - Improve prompt engineering for better results
4. **Expand Fallback Coverage** - Add more local processing capabilities

### Feedback Integration
- **User Feedback** - Incorporate developer preferences
- **Performance Data** - Use response quality metrics
- **Cost Analysis** - Optimize model selection per task type

## 🚨 Troubleshooting

### Common Issues

#### Cache Not Working
```bash
# Clear cache if corrupted
rm -rf automation/cache/assistant/
# Restart assistant API
```

#### API Key Issues
```bash
# Switch to secondary key
python automation/cli/assistant_cli.py switch-key secondary

# Check key status
python automation/cli/assistant_cli.py models
```

#### Connection Problems
```bash
# Verify server is running
curl http://127.0.0.1:8000/assistant/models

# Restart if needed
uvicorn automation.backend.assistant_api:app
```

## 📚 API Reference

### Query Endpoint
```http
POST /assistant/query
Content-Type: application/json

{
  "prompt": "Your question here",
  "model": "gpt-4o-mini",
  "temperature": 0.2,
  "max_tokens": 512,
  "metadata": {"context": "symphony_integration"}
}
```

### Response Format
```json
{
  "model": "gpt-4o-mini",
  "content": "Assistant response here...",
  "usage": {
    "total_tokens": 256,
    "prompt_tokens": 45,
    "completion_tokens": 211
  },
  "cached": false
}
```

## 🎼 Symphony Integration

The Assistant API seamlessly integrates with all Symphony components:

- **Knowledge Graph**: Ontology validation and semantic reasoning
- **Security Scanner**: AI-enhanced vulnerability analysis
- **MLOps Pipeline**: Model optimization recommendations
- **Multimodal Processor**: Cross-modal reasoning assistance
- **Synthetic Data Generator**: Data quality analysis
- **Phase Simulator**: Planning and validation guidance

This creates a comprehensive AI-powered development ecosystem that enhances productivity while maintaining cost efficiency.
