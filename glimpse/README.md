# Glimpse Preflight System

A side-effect-free preview system for AI outputs that ensures alignment with user intent before execution.

## Overview

Glimpse provides real-time previews of AI outputs, allowing users to review and adjust their inputs before committing to any actions. This prevents misalignment between intent and results while maintaining privacy and user control.

## Key Features

### Two-Try Flow
1. **First Preview**: Shows sample output and essence of the response
2. **Adjustment Phase**: User can modify their input based on the preview
3. **Second Preview**: Confirms the adjusted input
4. **Commit Decision**: User chooses to proceed or start over

### Privacy-First Design
- **PrivacyGuard**: Ensures no side effects until explicit commit
- **Ephemeral Previews**: All previews can be discarded without persistence
- **Minimal Persistence**: Only committed actions are saved

### Latency Awareness
- **Real-time Status**: Transparent updates on processing progress
- **Graceful Degradation**: Adapts to high-latency scenarios
- **Essence-Only Mode**: Shows only essential information when latency is high

### User Control
- **Transparent Indicators**: Clear status messages and progress tracking
- **No Silent Actions**: All operations require explicit user confirmation
- **Flexible Adjustments**: Users can modify inputs at any time before commit

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# The glimpse system is part of the Echoes project
# Ensure you're in the project root directory
```

## Quick Start

### Basic Usage

```python
from glimpse.Glimpse import GlimpseEngine, Draft

# Initialize the Glimpse
engine = GlimpseEngine()

# Create a draft
draft = Draft(
    input_text="Write an email to customers about the new feature",
    goal="inform users about update",
    constraints="tone: professional | length: brief"
)

# Get a preview
result = await Glimpse.glimpse(draft)

print(f"Status: {result.status}")
print(f"Sample: {result.sample}")
print(f"Essence: {result.essence}")

# If aligned, commit the action
if result.status == "aligned":
    Glimpse.commit(draft)
```

### Interactive Mode

```python
# Run the full interactive assistant
python assistant_v2_core.py

# Enable preflight mode
> preflight on

# Set your intent anchors
> anchors

# Send a message to see the preview
> Write an email to customers about our new feature

# You'll see:
# — Glimpse 1 —
# Status: aligned
# Sample: Dear valued customer, ...
# Essence: Professional notification about new feature

# Choose to proceed or adjust
> Proceed with commit? [y/N]: y
```

## Advanced Features

### Clarifier System

The clarifier system detects ambiguity in user input and asks targeted questions:

```python
from glimpse.clarifier_engine import ClarifierEngine

clarifier = ClarifierEngine()

# Detect ambiguities
clarifiers = clarifier.detect_ambiguity(
    "Write an email to customers",
    "",
    ""
)

# Returns clarifiers for audience, tone, and format
for c in clarifiers:
    print(c.format_question())
# Output:
# Clarifier: Is this for customers or internal team? [customers | internal] (default: internal)
# Clarifier: Should this be formal or informal? [formal | informal] (default: informal)
# Clarifier: What format would you prefer? [bullet points | paragraphs | numbered list] (default: bullet points)
```

### Performance Optimization

For high-latency scenarios, enable performance optimizations:

```python
from glimpse.performance_optimizer import PerformanceOptimizer

optimizer = PerformanceOptimizer(
    cache_size=1000,  # Number of cached results
    max_concurrent=10  # Maximum concurrent requests
)

# Use optimized glimpse
result, exec_time = await optimizer.optimized_glimpse(
    draft,
    sampler_function
)

# Batch processing for multiple requests
drafts = [draft1, draft2, draft3]
results = await optimizer.batch_glimpses(drafts, sampler_function)
```

### Essence-Only Mode

Automatically switch to essence-only mode for high latency:

```python
# Enable essence-only mode manually
Glimpse.set_essence_only(True)

# Or let the system decide based on latency
if avg_latency > 0.8:  # 800ms threshold
    Glimpse.set_essence_only(True)
```

## API Reference

### Core Classes

#### `Draft`
Represents a user input draft.

```python
@dataclass
class Draft:
    input_text: str
    goal: str
    constraints: str
```

#### `GlimpseResult`
Contains the result of a glimpse operation.

```python
@dataclass
class GlimpseResult:
    attempt: int
    status: str  # "aligned", "not_aligned", "stale", "redial"
    sample: str
    essence: str
    delta: Optional[str]
    stale: bool
    status_history: List[str]
```

#### `GlimpseEngine`
Main Glimpse for generating previews.

```python
class GlimpseEngine:
    def __init__(self, sampler=None, latency_monitor=None, privacy_guard=None):
        ...
    
    async def glimpse(self, draft: Draft) -> GlimpseResult:
        """Generate a preview of the draft"""
        ...
    
    def commit(self, draft: Draft):
        """Commit the draft (execute side effects)"""
        ...
    
    def cancel(self):
        """Cancel the current glimpse operation"""
        ...
    
    def set_essence_only(self, enabled: bool):
        """Enable or disable essence-only mode"""
        ...
```

### Status Types

- **`aligned`**: Preview matches user intent
- **`not_aligned`**: Preview needs adjustment
- **`stale`**: Result may be outdated due to latency
- **`redial`**: Too many attempts, start over

### Configuration Options

#### Latency Thresholds

```python
# Default thresholds (in milliseconds)
t1 = 100  # Initial trying status
t2 = 300  # Degraded performance
t3 = 800  # Offer essence-only mode
t4 = 2000  # Mark as stale
```

#### Privacy Settings

```python
# Custom commit handler
def my_commit_handler(draft: Draft):
    # Custom persistence logic
    save_to_database(draft)

privacy_guard = PrivacyGuard(on_commit=my_commit_handler)
engine = GlimpseEngine(privacy_guard=privacy_guard)
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/glimpse/ -v

# Run specific test suites
pytest tests/glimpse/test_glimpse_glimpse_core.py -v
pytest tests/glimpse/test_glimpse_edge_cases.py -v

# Run with coverage
pytest tests/glimpse/ --cov=glimpse --cov-report=html
```

### Test Coverage

The test suite covers:
- Two-tries logic and redial behavior
- Latency thresholds and stale handling
- Cancel-on-edit debounce
- Clarifier path activation
- Essence-only mode toggling
- Edge cases (null inputs, boundary values, concurrency)
- Performance optimization features

## Examples

### Example 1: Email Generation

```python
from glimpse.Glimpse import GlimpseEngine, Draft

engine = GlimpseEngine()

draft = Draft(
    input_text="Tell customers about our new AI features",
    goal="announce product update",
    constraints="audience: customers | tone: professional | length: brief"
)

result = await Glimpse.glimpse(draft)
print(result.sample)
# Output: "We're excited to announce our new AI-powered features..."
```

### Example 2: Code Documentation

```python
draft = Draft(
    input_text="Document this Python function",
    goal="generate docstring",
    constraints="format: structured | language: technical"
)

result = await Glimpse.glimpse(draft)
print(result.essence)
# Output: "Generate comprehensive technical documentation..."
```

### Example 3: High-Latency Handling

```python
from glimpse.performance_optimizer import PerformanceOptimizer

optimizer = PerformanceOptimizer()
optimizer.enable_optimization(True)

# Simulate high latency
async def slow_sampler(draft):
    await asyncio.sleep(1.5)  # 1.5 second delay
    return generate_sample(draft)

result, exec_time = await optimizer.optimized_glimpse(draft, slow_sampler)

# System automatically suggests essence-only mode
if optimizer.adaptive_essence_only(exec_time):
    Glimpse.set_essence_only(True)
```

## Best Practices

### 1. Clear Intent Specification
Always provide clear goals and constraints:
```python
draft = Draft(
    input_text="Explain the concept",
    goal="educate user",  # Clear goal
    constraints="audience: beginners | tone: simple | length: detailed"  # Specific constraints
)
```

### 2. Handle Latency Gracefully
```python
try:
    result = await Glimpse.glimpse(draft)
except asyncio.TimeoutError:
    # Handle high latency scenarios
    Glimpse.set_essence_only(True)
    result = await Glimpse.glimpse(draft)
```

### 3. Use Clarifiers for Ambiguity
```python
if result.delta and "Clarifier:" in result.delta:
    # Ask user for clarification
    response = input(result.delta + ": ")
    # Update constraints based on response
    draft.constraints = clarifier_engine.apply_clarifier_response(
        clarifier, response, draft.constraints
    )
```

### 4. Monitor Performance
```python
metrics = optimizer.get_metrics()
print(f"Cache hit rate: {metrics.cache_hit_rate:.2%}")
print(f"Average latency: {metrics.avg_latency:.3f}s")
print(f"Failed requests: {metrics.failed_requests}")
```

## Troubleshooting

### Common Issues

1. **"STATUS_RETRY is not defined"**
   - Ensure the status constants are imported at the top of the file
   - Check that the constants are defined before use

2. **"max_tokens is not supported"**
   - Use `max_completion_tokens` for o3 models
   - Use conditional logic based on model type

3. **High latency warnings**
   - Enable performance optimization
   - Use essence-only mode for high-latency scenarios
   - Consider caching frequently used results

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run glimpse with debug output
result = await Glimpse.glimpse(draft)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is part of the Echoes AI Assistant platform. See the main project LICENSE for details.

## Support

For questions and support:
- Check the documentation
- Review the test cases for examples
- Open an issue on the project repository
