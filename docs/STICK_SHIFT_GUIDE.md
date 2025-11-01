# Stick Shift Controller - Adaptive AI Behavior Guide

## Overview

The **Stick Shift Controller** is an innovative control system for adaptive AI behavior, inspired by:
- **Ableton's grid quantization system** (1/8th, 1/16th triplet, dotted notes)
- **Manual transmission** (downshift for power, upshift for efficiency)

This creates **versatile AI model behavior without extensive parameterization**.

## Core Concept

### The Metaphor

**Audio Engineering (Ableton Grid)**:
- Different grid resolutions (1/16th, 1/8th, 1/4th)
- Time signatures (straight 4/4, triplet 3/4, dotted 6/8)
- Quantization strength (70%-90%) creates controlled "swing"

**Manual Transmission**:
- **Downshift**: High RPM, aggressive, detailed processing
- **Upshift**: Low RPM, smooth, efficient processing
- **Gear selection**: Match Glimpse power to road conditions

**AI Behavior**:
- **Lower gears**: Deep inference, high detail, odd time signatures
- **Higher gears**: Broad strokes, efficient, smooth processing
- **Quantization**: Creates natural variation, not robotic

## The Five Gears

### FIRST Gear - Maximum Detail
```
Grid: 1/16th triplet
Time Signature: 3/4 (triplet)
Quantization: 90%
RPM: 8000
Style: aggressive_detailed
```

**Use for**:
- Complex refactoring
- Critical architecture decisions
- Deep code analysis
- High-stakes changes

**Characteristics**:
- Maximum inference depth (5 levels)
- Tight quantization (controlled randomness)
- Low temperature (precise)
- High token count (2000)

### SECOND Gear - High Detail
```
Grid: 1/16th
Time Signature: 5/4 (syncopated)
Quantization: 85%
RPM: 6000
Style: detailed
```

**Use for**:
- Code refactoring
- Performance optimization
- Bug fixing
- Detailed analysis

**Characteristics**:
- Deep inference (4 levels)
- Syncopated rhythm (off-beat processing)
- Moderate temperature
- Good token count (1500)

### THIRD Gear - Balanced
```
Grid: 1/8th
Time Signature: 4/4 (straight)
Quantization: 80%
RPM: 4000
Style: balanced
```

**Use for**:
- General tasks
- Code organization
- Standard refactoring
- Most workflows

**Characteristics**:
- Medium inference (3 levels)
- Straight rhythm (predictable)
- Balanced temperature
- Standard tokens (1000)

### FOURTH Gear - Efficient
```
Grid: 1/4th dotted
Time Signature: 6/8 (dotted)
Quantization: 75%
RPM: 2500
Style: efficient_smooth
```

**Use for**:
- Workflow analysis
- Documentation
- Simple updates
- Validation

**Characteristics**:
- Light inference (2 levels)
- Dotted rhythm (smooth flow)
- Higher temperature (creative)
- Moderate tokens (750)

### FIFTH Gear - Broad Strokes
```
Grid: 1/4th
Time Signature: 4/4 (straight)
Quantization: 70%
RPM: 1500
Style: broad_strokes
```

**Use for**:
- High-level planning
- Simple tasks
- Quick scans
- Overview generation

**Characteristics**:
- Minimal inference (1 level)
- Maximum swing (most variation)
- High temperature (most creative)
- Low tokens (500)

## Quantization & Swing

### What is Quantization?

In Ableton, quantization aligns notes to the grid at a certain strength:
- **100%**: Perfect alignment, robotic
- **80%**: Slight deviation, natural feel
- **70%**: More deviation, "swing" effect

In AI, quantization creates controlled randomness:
```python
base_behavior = 1.0
swing = (1.0 - quantization) * random.uniform(-0.2, 0.2)
behavior = base_behavior + swing
```

**Result**: Natural, non-robotic AI behavior with controlled variation.

### Time Signatures

- **4/4 (Straight)**: Predictable, standard processing
- **3/4 (Triplet)**: Odd time, creates swing effect
- **6/8 (Dotted)**: Compound meter, smooth flow
- **5/4 (Syncopated)**: Off-beat, unpredictable

These create different "rhythms" in AI processing.

## Usage

### Basic Usage

```python
from app.core import StickShiftController, Gear

# Create controller
controller = StickShiftController(starting_gear=Gear.THIRD)

# Manual shift
controller.shift_to(Gear.SECOND)

# Auto shift based on complexity
controller.auto_shift(task_complexity=0.8)

# Get processing config
config = controller.get_processing_config()
```

### Automatic Integration

The stick shift is **automatically integrated** into Lumina:

```python
from app.core import execute_task

# Automatically calculates complexity and shifts gears
result = await execute_task(
    "Use assistant to refactor complex module"
)
```

**What happens**:
1. Task complexity calculated: 0.75
2. Auto-shifts to SECOND gear
3. Applies 1/16th grid, 85% quantization
4. Uses syncopated time signature
5. Sets depth=4, RPM=6000

### Manual Control

```python
from app.core import create_stick_shift, Gear

controller = create_stick_shift(Gear.THIRD)

# Downshift for more detail
controller.downshift()  # → SECOND gear

# Downshift again
controller.downshift()  # → FIRST gear

# Upshift for efficiency
controller.upshift()    # → SECOND gear
controller.upshift()    # → THIRD gear
```

### Shift Modes

**Boost Mode** - Maximum power:
```python
config = controller.boost_mode()
# Downshifts + increases RPM 30%
# For critical/complex phases
```

**Cruise Mode** - Smooth efficiency:
```python
config = controller.cruise_mode()
# Upshifts to smooth gear
# For validation/checking
```

## Processing Configuration

Each gear provides complete AI configuration:

```python
config = controller.get_processing_config()

{
    'gear': 'SECOND',
    'grid_resolution': '1/16th',
    'time_signature': '5/4',
    'quantization': 0.85,
    'inference_depth': 4,
    'rpm': 6000,
    'style': 'detailed',
    'behavior_modifier': 1.023,  # Swing applied
    'temperature': 0.45,         # Low = precise
    'top_p': 0.80,
    'max_tokens': 1500,
}
```

## Integration with Lumina

### Autonomous Executor

The executor automatically:

1. **Calculates complexity**:
```python
complexity = calculate_task_complexity(
    request,
    context_size=len(files)
)
```

2. **Auto-shifts**:
```python
controller.auto_shift(complexity)
```

3. **Applies config to AI**:
```python
# Temperature, top_p, max_tokens all set by gear
```

4. **Dynamic shifting during execution**:
```python
# Boost mode for complex phases
# Cruise mode for validation
```

### Example Flow

```python
# User request
"Use assistant to refactor complex authentication module"

# Step 1: Calculate complexity → 0.85 (high)
# Step 2: Auto-shift → SECOND gear
# Step 3: Apply config:
#   - Grid: 1/16th
#   - Time: 5/4 syncopated
#   - Quantization: 85%
#   - Depth: 4
#   - RPM: 6000

# During execution:
#   - Critical phase detected → BOOST → FIRST gear
#   - Validation phase → CRUISE → THIRD gear
```

## Task Complexity Calculation

```python
from app.core import calculate_task_complexity

complexity = calculate_task_complexity(
    task_description="Use assistant to redesign architecture",
    context_size=150  # number of files
)
# → 0.9 (very complex)
# → Auto-selects FIRST gear
```

**Factors**:
- High complexity keywords: refactor, optimize, redesign (+0.3 each)
- Medium complexity: organize, improve, enhance (+0.2 each)
- Context size: >100 files (+0.3), >50 (+0.2), >10 (+0.1)

## Command Line Demo

```bash
python examples/stick_shift_demo.py
```

**Demos**:
1. Basic gear shifting
2. Processing config for each gear
3. Automatic gear selection
4. Boost and cruise modes
5. Task complexity calculation
6. Quantization swing effect
7. Interactive control

## API Reference

### StickShiftController

```python
controller = StickShiftController(starting_gear=Gear.THIRD)
```

**Methods**:
- `shift_to(gear, manual=True)` - Shift to specific gear
- `downshift()` - Shift down one gear
- `upshift()` - Shift up one gear
- `auto_shift(task_complexity)` - Auto-select gear
- `boost_mode()` - Activate boost
- `cruise_mode()` - Activate cruise
- `get_current_profile()` - Get gear profile
- `get_processing_config()` - Get AI config
- `get_status()` - Get status display

### Gear Enum

```python
from app.core import Gear

Gear.FIRST   # Maximum detail
Gear.SECOND  # High detail
Gear.THIRD   # Balanced
Gear.FOURTH  # Efficient
Gear.FIFTH   # Broad strokes
```

### Helper Functions

```python
from app.core import create_stick_shift, calculate_task_complexity

# Create controller
controller = create_stick_shift(Gear.THIRD)

# Calculate complexity
complexity = calculate_task_complexity(description, context_size)
```

## Examples

### Example 1: Manual Control

```python
from app.core import create_stick_shift, Gear

controller = create_stick_shift(Gear.THIRD)

print(controller.get_status())

# Need more detail?
controller.downshift()

# Get config
config = controller.get_processing_config()
print(f"Temperature: {config['temperature']}")
print(f"Max tokens: {config['max_tokens']}")
```

### Example 2: Auto Selection

```python
from app.core import StickShiftController, calculate_task_complexity

controller = StickShiftController()

# Different tasks
tasks = [
    "Fix typo in README",
    "Organize project structure",
    "Refactor authentication module",
    "Redesign entire architecture",
]

for task in tasks:
    complexity = calculate_task_complexity(task)
    controller.auto_shift(complexity)

    profile = controller.get_current_profile()
    print(f"{task}: {profile.gear.name} gear")
```

### Example 3: With Lumina

```python
from app.core import execute_task

# Automatically uses stick shift
result = await execute_task(
    "Use assistant to optimize performance across entire codebase"
)

# Stick shift automatically:
# - Calculated complexity: 0.9
# - Selected FIRST gear
# - Applied 1/16th triplet grid
# - Used 90% quantization
# - Set depth=5, RPM=8000
```

## Benefits

### 1. No Extensive Tuning Required

Traditional approach:
```python
# Manually tune for each task
model.temperature = 0.3
model.top_p = 0.85
model.max_tokens = 1500
# ... repeat for every task type
```

Stick shift approach:
```python
# Auto-selects optimal settings
controller.auto_shift(complexity)
```

### 2. Natural Variation

Quantization creates "swing" - controlled randomness that feels natural, not robotic.

### 3. Adaptive Behavior

Automatically adjusts processing style to task complexity:
- Simple tasks: Quick, broad strokes
- Complex tasks: Deep, detailed analysis

### 4. Intuitive Control

Musicians and drivers understand the metaphor:
- Downshift = more power/detail
- Upshift = more efficiency/smoothness

## Technical Details

### Grid Resolution Mapping

| Gear | Grid | Inference | Tokens | Temp |
|------|------|-----------|--------|------|
| 1st | 1/16th triplet | 5 | 2000 | 0.45 |
| 2nd | 1/16th | 4 | 1500 | 0.60 |
| 3rd | 1/8th | 3 | 1000 | 0.75 |
| 4th | 1/4th dotted | 2 | 750 | 0.90 |
| 5th | 1/4th | 1 | 500 | 1.05 |

### Quantization Effect

```python
# 90% quantization (tight control)
swing_range = (1.0 - 0.90) * 0.2 = 0.02
behavior = 1.0 ± 0.02  # Very consistent

# 70% quantization (loose control)
swing_range = (1.0 - 0.70) * 0.2 = 0.06
behavior = 1.0 ± 0.06  # More variation
```

### RPM Calculation

RPM represents processing intensity:
- 1st gear: 8000 RPM (maximum effort)
- 3rd gear: 4000 RPM (balanced)
- 5th gear: 1500 RPM (cruising)

Boost mode adds 30% RPM boost.

## Best Practices

1. **Start in THIRD gear** - Balanced default
2. **Use auto-shift** - Let complexity determine gear
3. **Trust the swing** - Quantization creates natural variation
4. **Monitor status** - Check gear selection
5. **Manual override** - Shift manually when needed

## Future Enhancements

- **Learn optimal gears** from feedback
- **Custom gear profiles** per user
- **Real-time gear shifting** during inference
- **Multi-model coordination** with different gears
- **Visual dashboard** showing RPM, gear, grid

## Summary

The Stick Shift Controller brings:

✅ **Adaptive behavior** without manual tuning
✅ **Natural variation** through quantization
✅ **Intuitive control** via familiar metaphors
✅ **Automatic optimization** based on complexity
✅ **Dynamic adjustment** during execution

**Get started:**
```bash
python examples/stick_shift_demo.py
```

Or use automatically with Lumina:
```python
from app.core import execute_task
result = await execute_task("Your request here")
```

🏎️ **Shift gears intelligently. Process adaptively.** 🏎️
