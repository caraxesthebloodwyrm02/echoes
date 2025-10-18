# GlimpsePreview System - Architecture Documentation

## 🏛️ System Architecture

### Overview

The GlimpsePreview System is built on a modular, layered architecture that separates concerns while enabling seamless integration. The system processes input events, tracks trajectories, generates predictions, and renders visual previews—all in real-time.

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
│              (demo_text_editor, demo_code_editor)           │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              GlimpsePreview Orchestrator                  │
│                  (realtime_preview.py)                      │
│  - Lifecycle management                                     │
│  - Component coordination                                   │
│  - Event callbacks                                          │
└─────┬──────────┬──────────┬──────────┬─────────────────────┘
      │          │          │          │
      ▼          ▼          ▼          ▼
┌──────────┐ ┌─────────┐ ┌────────┐ ┌──────────────┐
│Trajectory│ │  Input  │ │Visual  │ │  Security    │
│  Engine  │ │ Adapter │ │Renderer│ │ Integration  │
└──────────┘ └─────────┘ └────────┘ └──────────────┘
      │          │          │          │
      ▼          ▼          ▼          ▼
┌──────────────────────────────────────────────────────────────┐
│                     Data Layer                               │
│  - Trajectory points                                         │
│  - Input events                                              │
│  - Visual frames                                             │
│  - Security contexts                                         │
└──────────────────────────────────────────────────────────────┘
```

## 🧩 Core Components

### 1. Trajectory Engine (`core_trajectory.py`)

**Purpose**: Track and analyze the trajectory of work in real-time.

**Key Classes**:
- `TrajectoryPoint`: Single point in trajectory with metadata
- `TrajectorySegment`: Coherent segment with consistent direction
- `TrajectoryEngine`: Main engine for tracking and analysis

**Key Algorithms**:
```python
Direction Analysis:
    - Compare recent content lengths
    - Calculate trend and variance
    - Classify: expanding, converging, pivoting, stable, uncertain

Confidence Computation:
    - Measure direction consistency
    - More consistent = higher confidence
    - Range: 0.0 to 1.0

Cause-Effect Chain:
    - Track last N points
    - Build backward-looking chain
    - Show what led to current state

Predictions:
    - Based on current direction and confidence
    - Generate probability-weighted next states
    - Lookahead configurable
```

**Data Flow**:
```
Input Content → Add Point → Analyze Direction → Compute Confidence
                    ↓
              Trace Cause-Effect → Update Segments → Generate Predictions
```

### 2. Input Adapter (`input_adapter.py`)

**Purpose**: Handle all input events and provide adaptive suggestions.

**Key Classes**:
- `InputEvent`: Single input event (insert, delete, replace, etc.)
- `AdaptationContext`: Context for suggestions and predictions
- `InputAdapter`: Main adapter managing input state

**Event Processing Pipeline**:
```
User Input → Event Type Classification → State Update → History Recording
                                            ↓
                                    Undo/Redo Stack Update
                                            ↓
                                    Generate Adaptation Context
                                            ↓
                                    Compute Metrics (velocity, intensity)
```

**Key Features**:
- Full undo/redo support with stack management
- Typing velocity tracking (chars/second)
- Edit intensity measurement (edits/second)
- Context-aware suggestions via registered providers
- Diff computation for content comparison

### 3. Visual Renderer (`visual_renderer.py`)

**Purpose**: Generate visual previews in multiple modes.

**Visualization Modes**:

#### Timeline Mode
```
Point 1 ─→ Point 2 ─→ Point 3 ─→ Point 4
   │          │          │          │
   ↓          ↓          ↓          ↓
Cause      Cause      Cause      Cause
Effect     Effect     Effect     Effect
Chain      Chain      Chain      Chain
```

#### Tree Mode
```
        Root Segment
           ├─→ Branch 1 (Expanding)
           ├─→ Branch 2 (Converging)
           └─→ Branch 3 (Stable)
```

#### Flow Mode
```
        ● ● ● ●
       ● ● ● ●
      ● ● ⬤ ● ●  ← Central flow with particles
       ● ● ● ●
        ● ● ● ●
```

#### Heatmap Mode
```
Grid showing editing intensity:
[Cold] ░░░░░░░░ [Warm] ▒▒▒▒▒▒ [Hot] ████████
```

**Rendering Pipeline**:
```
Trajectory Data → Mode Selection → Element Generation → Frame Creation
                                            ↓
                                    Color Mapping (based on direction)
                                            ↓
                                    Position Calculation
                                            ↓
                                    ASCII/JSON Export
```

### 4. Security Integration (`security_integration.py`)

**Purpose**: Integrate defensive security from `thon.py` module.

**Security Architecture**:
```
┌─────────────────────────────────────────────────────┐
│              Security Manager                       │
├─────────────────────────────────────────────────────┤
│  Dynamic Module Loading (thon.py)                   │
│         ↓                                           │
│  Orchestrator ← → Detector                          │
│         ↓              ↓                            │
│  Attractors      Shield Factor                      │
│  Jammers         Risk Assessment                    │
│         ↓              ↓                            │
│  Command Validation                                 │
│  Operation Validation                               │
└─────────────────────────────────────────────────────┘
```

**Shield Factor Computation**:
```python
shield = base_strength - penalty + boost

where:
  base_strength = avg_attractor_strength
  penalty = min(0.3 * high_jammers, 0.6)
  boost = environmental_factors
```

**Operation Validation Matrix**:
```
Shield Factor | Allowed Operations
─────────────┼───────────────────────────────
  0.0 - 0.3  | read, preview, visualize
  0.3 - 0.5  | + track, analyze
  0.5 - 0.7  | + suggest, adapt
  0.7 - 0.9  | + export, save
  0.9 - 1.0  | + execute, deploy
```

**Command Injection Prevention**:
```python
Suspicious Pattern Detection:
  - Shell metacharacters: ; || && $ ( ) ` > /
  - Dangerous commands: shutdown, rm, rm -rf

Whitelist Approach:
  - Only explicitly allowed commands pass
  - All others rejected by default

Length Validation:
  - Commands capped at MAX_SIMULATED_CMD_LENGTH
```

### 5. GlimpsePreview Orchestrator (`realtime_preview.py`)

**Purpose**: Main integration layer coordinating all components.

**State Machine**:
```
┌─────────┐  start()   ┌────────┐  process_input()  ┌─────────┐
│ Stopped │ ────────→  │ Active │ ←──────────────→  │ Working │
└─────────┘            └────────┘                   └─────────┘
     ↑                     │                              │
     │                     │ stop()                       │
     └─────────────────────┘                              │
                                                          │
                           auto_save() ←─────────────────┘
```

**Event Processing Flow**:
```
User Input Event
    ↓
Security Validation (if enabled)
    ↓
Input Adapter Processing
    ↓
Trajectory Point Creation
    ↓
Visual Preview Generation
    ↓
Suggestion/Prediction Generation
    ↓
Callback Triggering
    ↓
Result Package Assembly
    ↓
Auto-Save Check
    ↓
Return Result to User
```

**Configuration System**:
```python
PreviewConfiguration:
  - visualization_mode: timeline|tree|flow|heatmap
  - enable_security: bool
  - enable_predictions: bool
  - enable_suggestions: bool
  - trajectory_window_size: int
  - input_buffer_size: int
  - auto_save_interval: float
```

## 🔄 Data Flow Diagrams

### Complete System Flow

```
┌──────────────┐
│  User Input  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│           GlimpsePreview System                │
│                                                  │
│  ┌────────────────┐                             │
│  │ Security Check │ (if enabled)                │
│  └────────┬───────┘                             │
│           │                                      │
│           ▼                                      │
│  ┌────────────────┐        ┌─────────────────┐ │
│  │ Input Adapter  │───────→│ Trajectory      │ │
│  │                │        │ Engine          │ │
│  │ - Event Log    │        │                 │ │
│  │ - Undo/Redo    │        │ - Points        │ │
│  │ - Suggestions  │        │ - Segments      │ │
│  └────────────────┘        │ - Predictions   │ │
│           │                └─────────┬───────┘ │
│           │                          │         │
│           ▼                          │         │
│  ┌────────────────┐                 │         │
│  │ Visual         │←────────────────┘         │
│  │ Renderer       │                           │
│  │                │                           │
│  │ - Timeline     │                           │
│  │ - Tree         │                           │
│  │ - Flow         │                           │
│  │ - Heatmap      │                           │
│  └────────┬───────┘                           │
│           │                                    │
└───────────┼────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────┐
│  Output                      │
│  - Trajectory State          │
│  - Visual Preview            │
│  - Suggestions               │
│  - Predictions               │
│  - Security Report           │
└──────────────────────────────┘
```

### Security Integration Flow

```
┌─────────────────────────────────────────────────┐
│         Load thon.py Module                     │
│                                                 │
│  D:\thon.py ──→ Dynamic Import                  │
│                     ↓                           │
│              Orchestrator Creation              │
│                     ↓                           │
│              Detector Creation                  │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│         Security Assessment                     │
│                                                 │
│  Inspect Attractors                             │
│        ↓                                        │
│  Count High Jammers                             │
│        ↓                                        │
│  Check Consecutive Jams                         │
│        ↓                                        │
│  Compute Shield Factor                          │
│        ↓                                        │
│  Determine Risk Level                           │
│        ↓                                        │
│  Build Allowed Operations List                  │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│         Security Context                        │
│                                                 │
│  - shield_factor: float (0-1)                   │
│  - is_safe: bool                                │
│  - risk_level: low|medium|high                  │
│  - allowed_operations: list                     │
└─────────────────────────────────────────────────┘
```

## 🔧 Extension Points

### Custom Direction Analyzers

Register domain-specific analyzers:

```python
def code_analyzer(points):
    """Analyze code-specific patterns"""
    # Your logic here
    return TrajectoryDirection.EXPANDING

trajectory_engine.register_analyzer(code_analyzer)
```

### Custom Suggestion Providers

Add intelligent suggestion systems:

```python
def ml_suggester(context):
    """ML-based suggestions"""
    # Your ML model here
    return ["suggestion1", "suggestion2"]

input_adapter.register_suggestion_provider(ml_suggester)
```

### Event Callbacks

Hook into system events:

```python
def on_trajectory_change(data):
    """React to trajectory changes"""
    # Your logic here

realtime_preview.register_event_callback(on_trajectory_change)
```

## 📊 Performance Considerations

### Memory Management

- **Trajectory Window**: Configurable size (default: 100 points)
- **Input Buffer**: Configurable size (default: 50 events)
- **Frame Limit**: Export animations with frame limits
- **Deque Usage**: Automatic old data pruning

### Computational Complexity

```
Operation                  | Time Complexity | Space Complexity
─────────────────────────┼─────────────────┼─────────────────
Add Trajectory Point     | O(1) amortized  | O(1)
Analyze Direction        | O(k) k=recent   | O(1)
Generate Predictions     | O(1)            | O(1)
Process Input Event      | O(1)            | O(1)
Render Timeline          | O(n) n=points   | O(n)
Render Tree              | O(m) m=segments | O(m)
```

### Optimization Strategies

1. **Lazy Evaluation**: Predictions generated only when requested
2. **Caching**: Frame caching for repeated renders
3. **Pruning**: Automatic cleanup of old data
4. **Async Operations**: Background auto-save
5. **Efficient Data Structures**: Deques for rolling windows

## 🛡️ Security Model

### Threat Model

**Protected Against**:
- Command injection attacks
- Unauthorized file system access
- Resource exhaustion
- Malicious input patterns

**Trust Boundaries**:
```
Trusted:
  - Core system components
  - thon.py security module
  - Configuration files

Untrusted:
  - User input
  - External commands
  - Dynamic content
```

### Defense in Depth

```
Layer 1: Input Validation
  ↓
Layer 2: Security Context Assessment
  ↓
Layer 3: Operation Authorization
  ↓
Layer 4: Command Sanitization
  ↓
Layer 5: Execution Monitoring (thon.py)
```

## 🔮 Future Architecture Enhancements

### Planned Improvements

1. **Distributed Architecture**
   - Multi-user trajectory merging
   - Cloud synchronization
   - Real-time collaboration

2. **Machine Learning Integration**
   - Neural network predictors
   - Personalized analyzers
   - Pattern recognition

3. **Advanced Visualization**
   - 3D trajectory rendering
   - WebGL/Canvas integration
   - Interactive UI framework

4. **Performance Optimization**
   - JIT compilation for hot paths
   - GPU acceleration for rendering
   - Streaming architecture

5. **Enhanced Security**
   - Sandboxed execution
   - Capability-based security
   - Formal verification

## 📝 Design Principles

1. **Modularity**: Each component is independently testable
2. **Extensibility**: Plugin architecture via registration
3. **Safety**: Security-first design with thon.py integration
4. **Simplicity**: Pure Python, zero external dependencies
5. **Performance**: Efficient algorithms and data structures
6. **Usability**: Clear APIs and comprehensive documentation

---

This architecture supports the core vision: providing a real-time compass for creative and developmental work, enabling users to see where they're going based on where they've been.
