# Expanded Model Evaluation Test Suite

This comprehensive test suite addresses rate limiting issues and provides robust evaluation capabilities for AI language models with proper error handling, retry mechanisms, and performance monitoring.

## 🚀 Components

### 1. `expanded_evaluation_suite.py` - Main Evaluation Glimpse
- **Rate Limiting Detection**: Automatically detects and handles rate limiting
- **Exponential Backoff**: Implements intelligent retry with exponential backoff
- **Concurrent Processing**: Configurable concurrent request handling
- **Circuit Breaker Pattern**: Prevents cascade failures
- **Comprehensive Metrics**: Detailed performance and error tracking
- **Caching Support**: Avoids re-processing completed evaluations

### 2. `load_tester.py` - Load Testing & Rate Limit Discovery
- **Load Testing**: Tests model endpoints with various concurrency levels
- **Rate Limit Detection**: Identifies rate limiting thresholds
- **Stress Testing**: Finds optimal concurrency levels
- **Performance Metrics**: Throughput, latency, and error analysis

### 3. `performance_monitor.py` - System Resource Monitoring
- **Real-time Monitoring**: CPU, memory, disk, and network metrics
- **GPU Monitoring**: NVIDIA GPU utilization and temperature
- **Process Tracking**: Ollama process resource usage
- **Historical Analysis**: Performance trends over time

### 4. `evaluation_config.json` - Configuration Management
- **Rate Limiting Settings**: Configurable retry and backoff parameters
- **Model Selection**: Easy model switching and multi-model evaluation
- **Load Testing Options**: Configurable test parameters
- **Logging Configuration**: Customizable logging levels and outputs

## 📋 Prerequisites

```bash
# Install required packages
pip install psutil gputil

# Ensure Ollama is installed and running
ollama serve

# Pull required models
ollama pull mistral:7b-instruct
```

## 🔧 Configuration

Edit `evaluation_config.json` to customize behavior:

```json
{
  "rate_limiting": {
    "max_retries": 5,
    "base_delay": 2.0,
    "max_delay": 120.0,
    "backoff_factor": 1.5,
    "rate_limit_window": 60.0,
    "max_requests_per_window": 20,
    "concurrent_limit": 2
  },
  "models": ["mistral:7b-instruct"],
  "evaluation": {
    "enable_metrics": true,
    "timeout_per_question": 600
  }
}
```

## 🚀 Usage

### Basic Evaluation
```bash
python expanded_evaluation_suite.py
```

### Load Testing
```bash
python load_tester.py
```

### Performance Monitoring
```bash
python performance_monitor.py
```

### Custom Configuration
```bash
# Use custom config file
python expanded_evaluation_suite.py --config my_config.json
```

## 📊 Rate Limiting Features

### Automatic Detection
- Monitors HTTP status codes (429)
- Detects rate limit messages in responses
- Tracks request frequency and patterns

### Intelligent Retry
- Exponential backoff with jitter
- Configurable retry limits
- Circuit breaker pattern for cascade prevention

### Adaptive Throttling
- Dynamic request rate adjustment
- Window-based rate limiting
- Concurrent request management

## 📈 Metrics & Monitoring

### Performance Metrics
- Response times (avg, p95, p99)
- Success/failure rates
- Throughput (requests/second)
- Error categorization

### System Metrics
- CPU utilization
- Memory usage
- GPU utilization (if available)
- Network I/O
- Disk I/O

### Model-Specific Metrics
- Tokens per second
- Prompt vs response length ratios
- Model-specific error patterns

## 🛠️ Troubleshooting

### Common Rate Limiting Issues

1. **High Rate Limit Hits**
   ```
   Solution: Increase base_delay and reduce max_requests_per_window
   ```

2. **Timeout Errors**
   ```
   Solution: Increase timeout_per_question and reduce concurrent_limit
   ```

3. **Memory Issues**
   ```
   Solution: Reduce concurrent_limit and monitor with performance_monitor.py
   ```

### Debug Mode
```bash
# Enable verbose logging
export PYTHONPATH=$PYTHONPATH:.
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
python expanded_evaluation_suite.py
```

## 📁 Output Structure

```
model_eval/
├── evaluations/
│   ├── run_20241218_143000/          # Timestamped evaluation run
│   │   ├── mistral_7b-instruct/      # Model-specific results
│   │   │   ├── 01_context_understanding.md
│   │   │   ├── 02_code_generation.md
│   │   │   └── ...
│   │   └── evaluation_metrics.json   # Comprehensive metrics
├── load_test_results/                 # Load testing outputs
├── performance_metrics_*.json         # System monitoring data
├── model_eval.log                     # Application logs
└── evaluation_config.json             # Configuration file
```

## 🔍 Interpreting Results

### Success Metrics
- **Success Rate > 95%**: Excellent performance
- **Success Rate 85-95%**: Good performance, minor issues
- **Success Rate < 85%**: Needs optimization

### Rate Limiting Indicators
- **Rate Limit Hits**: Number of detected rate limiting events
- **Retry Attempts**: How often the system had to retry
- **Average Backoff**: Time spent waiting due to rate limits

### Performance Benchmarks
- **Response Time < 30s**: Fast model performance
- **Response Time 30-60s**: Acceptable performance
- **Response Time > 60s**: May need optimization

## 🤝 Contributing

1. **Report Issues**: Use the issue tracker for bugs and rate limiting problems
2. **Performance Data**: Share your evaluation metrics for comparison
3. **Optimizations**: Submit improvements to rate limiting algorithms

## 📄 License

This test suite is part of the Glimpse project evaluation framework.
