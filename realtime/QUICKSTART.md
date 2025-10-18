# Quick Start Guide - Realtime Preview System

## 🚀 5-Minute Quick Start

### Step 1: Launch the System

Open PowerShell and navigate to the directory:

```powershell
cd D:\realtime
```

### Step 2: Run the Interactive Launcher

```powershell
python launcher.py
```

This will present you with an interactive menu:

```
1. Run Text Editor Demo
2. Run Code Editor Demo
3. Run Test Suite
4. Security Check
5. Interactive Playground
6. View Documentation
7. System Information
0. Exit
```

### Step 3: Try the Text Editor Demo

Select option `1` to see realtime trajectory visualization for writing.

You'll see:
- Direction analysis (expanding, converging, pivoting, etc.)
- Confidence scores
- Predictions for next steps
- Cause-effect chains
- Visual ASCII preview

### Step 4: Try the Interactive Playground

Select option `5` to experiment with your own input:

1. Choose a visualization mode (timeline, tree, flow, or heatmap)
2. Type text and see real-time trajectory updates
3. Type `preview` to see the visualization
4. Type `state` to see system state
5. Type `quit` to exit

## 🎯 Direct Command Examples

### Run Text Demo Directly

```powershell
python demo_text_editor.py
```

### Run Code Demo Directly

```powershell
python demo_code_editor.py
```

### Run Tests

```powershell
python test_suite.py
```

## 📝 Quick Code Example

Create a file `my_test.py`:

```python
from realtime_preview import create_preview_system

# Create system
system = create_preview_system(mode="timeline")

# Start
system.start()

# Type something
system.process_input(action="insert", position=0, text="Hello world")

# See what's happening
state = system.get_full_state()
print(f"Direction: {state['trajectory']['current_direction']}")

# Get visual preview
preview = system.get_current_preview()
print(preview)

# Stop
system.stop()
```

Run it:

```powershell
python my_test.py
```

## 🔒 Security Check

Before deploying, always run a security check:

```powershell
python -c "from security_integration import quick_security_check; print('Safe!' if quick_security_check() else 'Check failed')"
```

Or use the launcher menu option 4.

## 📊 Understanding the Output

### Direction Values
- **expanding**: Building up, adding content
- **converging**: Narrowing down, focusing
- **pivoting**: Changing direction
- **stable**: Maintaining current course
- **uncertain**: No clear pattern

### Confidence Score
- **0.0 - 0.3**: Low confidence, uncertain trajectory
- **0.3 - 0.7**: Medium confidence
- **0.7 - 1.0**: High confidence, clear direction

### Shield Factor (Security)
- **0.0 - 0.3**: High risk, limited operations
- **0.3 - 0.7**: Medium risk
- **0.7 - 1.0**: Low risk, most operations allowed

## 🎨 Visualization Modes

Try different modes to see what works best:

```python
system.set_visualization_mode("timeline")  # Linear progression
system.set_visualization_mode("tree")      # Branching structure
system.set_visualization_mode("flow")      # Momentum visualization
system.set_visualization_mode("heatmap")   # Editing intensity
```

## 💾 Exporting Results

```python
# Export entire session
system.export_session("D:/realtime/my_session")

# This creates:
# - session_state.json
# - trajectory.json
# - animation.json
# - security_report.json (if security enabled)
```

## ⚡ Tips for Best Results

1. **Start the system before processing input**: Always call `system.start()` first
2. **Use appropriate modes**: Timeline for linear work, Tree for branching, Flow for momentum
3. **Enable security for production**: Set `enable_security=True`
4. **Register custom analyzers**: Add domain-specific direction analysis
5. **Check exports folder**: All demos save to `exports/` directory

## 🆘 Troubleshooting

### "System not active" error
```python
system.start()  # Always start first!
```

### Security check fails
```python
# Check thon.py is in parent directory
# Or disable security for testing:
system = create_preview_system(enable_security=False)
```

### Import errors
```python
# Make sure you're in the D:\realtime directory
cd D:\realtime
python your_script.py
```

## 📚 Next Steps

1. Read the full [README.md](README.md)
2. Explore the demo files to understand patterns
3. Run the test suite to see all features
4. Create your own custom analyzers and renderers
5. Integrate into your own applications

---

**Remember**: The system shows you where you're going based on where you've been. Use it as your creative compass! 🧭
