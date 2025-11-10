# ⚡ ECHOES PERFORMANCE OPTIMIZATION GUIDE
## From Functional to Lightning-Fast

---

## 🎯 Performance Targets

| Metric | Target | Critical Path |
|--------|--------|---------------|
| API Response Time | <200ms | User-facing endpoints |
| Statistical Operations | <10ms | Core computations |
| Docker Startup | <5s | Container initialization |
| Memory Usage | <2GB baseline | Runtime efficiency |
| Throughput | 10,000+ req/min | Load handling |

---

## 🚀 TIER 1: IMMEDIATE WINS (Week 1)

### 1. Vectorization: Replace Loops with NumPy

**BEFORE (Slow):**
```python
def slow_mean(data):
    total = 0
    for x in data:
        total += x
    return total / len(data)
```

**AFTER (Fast):**
```python
def fast_mean(data):
    return np.mean(data)  # 100x faster for large arrays
```

### 2. Numba JIT Compilation

Add `@numba.jit` to computational hotspots:

```python
import numba

@numba.jit(nopython=True, cache=True)
def fast_pdf(x, mean, std):
    """JIT-compiled normal PDF - 10-50x speedup."""
    z = (x - mean) / std
    return np.exp(-0.5 * z**2) / (std * np.sqrt(2 * np.pi))

# First call compiles, subsequent calls are lightning fast
result = fast_pdf(data, 0, 1)
```

**Installation:**
```bash
pip install numba
```

### 3. Lazy Imports

Only import heavy modules when needed:

```python
# BEFORE: Import at module level (slow startup)
import scipy.special
import matplotlib.pyplot as plt

# AFTER: Import in function (fast startup)
def compute_gamma(x):
    from scipy import special  # Only loaded when called
    return special.gamma(x)
```

### 4. Caching with functools

Cache expensive computations:

```python
from functools import lru_cache

@lru_cache(maxsize=1024)
def expensive_calculation(n):
    """Cached for repeated calls with same input."""
    # Complex calculation here
    return result

# First call: slow
# Subsequent calls with same n: instant
```

---

## 🔥 TIER 2: ALGORITHMIC OPTIMIZATION (Week 2-3)

### 1. Use Optimized Algorithms

```python
# SLOW: O(n²) algorithm
def slow_correlation(x, y):
    result = []
    for i in range(len(x)):
        for j in range(len(y)):
            result.append(x[i] * y[j])
    return sum(result)

# FAST: O(n) using NumPy
def fast_correlation(x, y):
    return np.corrcoef(x, y)[0, 1]
```

### 2. Avoid Unnecessary Copies

```python
# SLOW: Creates multiple copies
def slow_normalize(data):
    data = data.copy()
    data = data - data.mean()
    data = data / data.std()
    return data

# FAST: In-place operations
def fast_normalize(data):
    data = np.asarray(data)
    data -= data.mean()
    data /= data.std()
    return data
```

### 3. Pre-allocate Arrays

```python
# SLOW: Growing list
def slow_cumsum(data):
    result = []
    total = 0
    for x in data:
        total += x
        result.append(total)
    return result

# FAST: Pre-allocated array
def fast_cumsum(data):
    result = np.empty_like(data)
    total = 0
    for i, x in enumerate(data):
        total += x
        result[i] = total
    return result

# FASTEST: Built-in
def fastest_cumsum(data):
    return np.cumsum(data)
```

---

## 💎 TIER 3: ADVANCED OPTIMIZATION (Week 4+)

### 1. Parallel Processing with Multiprocessing

```python
from multiprocessing import Pool
import numpy as np

def process_chunk(chunk):
    """Process data chunk independently."""
    return np.mean(chunk), np.std(chunk)

def parallel_statistics(data, n_workers=4):
    """Distribute work across CPU cores."""
    chunks = np.array_split(data, n_workers)
    
    with Pool(n_workers) as pool:
        results = pool.map(process_chunk, chunks)
    
    # Combine results
    means, stds = zip(*results)
    return np.mean(means), np.mean(stds)

# 4x speedup on 4-core machine
```

### 2. Memory-Mapped Files for Large Data

```python
def process_large_file(filename):
    """Process files larger than RAM."""
    # Memory-mapped array - doesn't load into RAM
    data = np.load(filename, mmap_mode='r')
    
    # Process in chunks
    chunk_size = 10000
    results = []
    
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        results.append(process_chunk(chunk))
    
    return np.concatenate(results)
```

### 3. GPU Acceleration with CuPy

```python
try:
    import cupy as cp
    USE_GPU = True
except ImportError:
    import numpy as cp
    USE_GPU = False

def gpu_accelerated_operation(data):
    """Automatically use GPU if available."""
    data_gpu = cp.asarray(data)
    result = cp.fft.fft(data_gpu)  # GPU FFT
    return cp.asnumpy(result)  # Back to CPU

# 10-100x speedup for large arrays
```

---

## 🐳 DOCKER OPTIMIZATION

### 1. Multi-Stage Build

```dockerfile
# Build stage
FROM python:3.12-slim as builder

WORKDIR /build
COPY requirements.txt .

# Install to custom location
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim

# Copy only installed packages
COPY --from=builder /install /usr/local

COPY . /app
WORKDIR /app

CMD ["python", "-m", "api.main"]
```

### 2. Optimize Layers

```dockerfile
# SLOW: Reinstalls dependencies on any code change
COPY . /app
RUN pip install -r requirements.txt

# FAST: Cache dependencies layer
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app  # Code changes don't rebuild dependencies
```

### 3. Use Alpine or Slim Images

```dockerfile
# BLOATED: 1.2GB
FROM python:3.12

# OPTIMIZED: 150MB
FROM python:3.12-alpine

# BALANCED: 300MB (better compatibility)
FROM python:3.12-slim
```

---

## 📊 BENCHMARKING & PROFILING

### 1. Profile Code Hotspots

```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code here
    result = expensive_operation()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 slowest functions

profile_function()
```

### 2. Line-by-Line Profiling

```python
from line_profiler import LineProfiler

@profile  # Decorate function to profile
def function_to_optimize():
    # Line-by-line timing
    result = []
    for i in range(1000):
        result.append(i ** 2)
    return result

# Run: kernprof -l -v script.py
```

### 3. Memory Profiling

```python
from memory_profiler import profile

@profile
def memory_hungry_function():
    big_list = [0] * (10 ** 7)  # Allocates ~80MB
    return sum(big_list)

# Run: python -m memory_profiler script.py
```

### 4. Automated Performance Tests

```python
import pytest
import time

@pytest.mark.performance
def test_api_response_time():
    """Ensure API meets <200ms target."""
    start = time.time()
    
    response = client.get('/health')
    
    elapsed = (time.time() - start) * 1000
    assert elapsed < 200, f"Response took {elapsed:.1f}ms (target: <200ms)"

@pytest.mark.performance
def test_statistical_operations():
    """Ensure core operations meet <10ms target."""
    import numpy as np
    from core import stats
    
    data = np.random.randn(10000)
    
    start = time.time()
    result = stats.mean(data)
    elapsed = (time.time() - start) * 1000
    
    assert elapsed < 10, f"Operation took {elapsed:.1f}ms (target: <10ms)"
```

---

## 🎯 PERFORMANCE CHECKLIST

### Before Committing Code:

- [ ] Replaced loops with vectorized NumPy operations
- [ ] Added `@numba.jit` to computational hotspots
- [ ] Used `@lru_cache` for expensive repeated calculations
- [ ] Avoided unnecessary array copies
- [ ] Pre-allocated arrays where possible
- [ ] Used lazy imports for heavy modules
- [ ] Profiled code to identify bottlenecks
- [ ] Added performance tests
- [ ] Documented any performance trade-offs

### API Optimization:

- [ ] Added request caching
- [ ] Implemented connection pooling
- [ ] Used async/await for I/O operations
- [ ] Added rate limiting
- [ ] Configured proper timeouts
- [ ] Enabled gzip compression
- [ ] Added health check endpoint

### Docker Optimization:

- [ ] Used multi-stage builds
- [ ] Optimized layer caching
- [ ] Minimized image size
- [ ] Set resource limits
- [ ] Added health checks
- [ ] Configured restart policies

---

## 📈 PERFORMANCE MONITORING

### Production Metrics to Track:

```python
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to track function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        
        # Log to monitoring system
        print(f"{func.__name__}: {elapsed*1000:.2f}ms")
        
        return result
    return wrapper

@monitor_performance
def api_endpoint():
    # Your code
    pass
```

### Set Up Alerts:

- Response time > 200ms
- Memory usage > 2GB
- CPU usage > 80%
- Error rate > 1%
- Container restarts

---

## 🏆 SUCCESS METRICS

Target achieved when:

✅ All API endpoints respond in <200ms (95th percentile)  
✅ Core statistical operations complete in <10ms  
✅ Docker container starts in <5 seconds  
✅ Memory usage stable at <2GB baseline  
✅ System handles 10,000+ requests/minute  
✅ Zero performance regressions in CI  

**Track with:**
```bash
# Response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Memory usage
docker stats echoes-production --no-stream

# Load test
locust -f locustfile.py --headless -u 1000 -r 100 --run-time 60s
```

---

## 🚀 OPTIMIZATION PRIORITY ORDER

1. **Vectorize** everything possible with NumPy
2. **JIT compile** computational hotspots with Numba
3. **Cache** expensive repeated calculations
4. **Profile** to find real bottlenecks (don't guess!)
5. **Parallelize** CPU-bound operations
6. **GPU accelerate** if needed for massive data
7. **Optimize Docker** for faster deployment

Remember: **Measure first, optimize second!**
