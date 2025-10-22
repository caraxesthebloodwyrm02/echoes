# Extension Examples — Glimpse Realtime

This document provides practical examples for extending the Glimpse pipeline with custom adapters, analyzers, and renderers.

---

## 1. Custom Input Adapter

### Use Case: Markdown-Aware Input Processing

Extend `InputAdapter` to provide markdown-specific suggestions and formatting:

```python
from input_adapter import InputAdapter, AdaptationContext
from typing import List
import re

class MarkdownInputAdapter(InputAdapter):
    """Input adapter with markdown-aware suggestions"""

    def __init__(self, buffer_size: int = 50):
        super().__init__(buffer_size)
        # Register markdown suggestion provider
        self.register_suggestion_provider(self._markdown_suggestions)

    def _markdown_suggestions(self, context: AdaptationContext) -> List[str]:
        """Generate markdown-specific suggestions"""
        content = context.current_content
        cursor = context.cursor_position

        suggestions = []

        # Get current line
        lines = content[:cursor].split('\n')
        current_line = lines[-1] if lines else ""

        # Heading completion
        if current_line.startswith('#'):
            level = len(re.match(r'^#+', current_line).group())
            suggestions.append(f"{'#' * level} Heading level {level}")

        # List continuation
        if re.match(r'^\s*[-*+]\s', current_line):
            suggestions.append("Continue list")
            suggestions.append("Nest list item")

        # Link template
        if '[' in current_line and ']' not in current_line:
            suggestions.append("[text](url)")

        # Code block
        if current_line.strip() == '```':
            suggestions.append("```python\n# code here\n```")
            suggestions.append("```javascript\n// code here\n```")

        return suggestions[:3]

# Usage
adapter = MarkdownInputAdapter()
orchestrator = GlimpseOrchestrator()
orchestrator.input_adapter = adapter
```

---

## 2. Custom Trajectory Analyzer

### Use Case: Code Complexity Tracking

Analyze trajectory to detect increasing code complexity:

```python
from core_trajectory import TrajectoryEngine, TrajectoryDirection, TrajectoryPoint
from typing import List
import re

class CodeComplexityAnalyzer:
    """Analyzes code complexity trends in trajectory"""

    def __init__(self):
        self.complexity_keywords = [
            'if', 'else', 'elif', 'for', 'while', 'try', 'except',
            'def', 'class', 'async', 'await', 'lambda'
        ]

    def analyze_direction(self, points: List[TrajectoryPoint]) -> TrajectoryDirection:
        """Determine trajectory based on code complexity"""
        if len(points) < 3:
            return TrajectoryDirection.UNCERTAIN

        recent = points[-5:]
        complexities = [self._compute_complexity(p.content) for p in recent]

        # Trend analysis
        if len(complexities) < 2:
            return TrajectoryDirection.UNCERTAIN

        trend = complexities[-1] - complexities[0]
        variance = max(complexities) - min(complexities)

        if trend > variance * 0.5:
            return TrajectoryDirection.EXPANDING  # Adding complexity
        elif trend < -variance * 0.5:
            return TrajectoryDirection.CONVERGING  # Simplifying
        elif variance > sum(complexities) / len(complexities) * 0.4:
            return TrajectoryDirection.PIVOTING  # Refactoring
        else:
            return TrajectoryDirection.STABLE

    def _compute_complexity(self, content: str) -> float:
        """Simple complexity metric based on control structures"""
        score = 0.0

        for keyword in self.complexity_keywords:
            # Count keyword occurrences
            score += len(re.findall(rf'\b{keyword}\b', content))

        # Nesting depth (approximate)
        max_indent = 0
        for line in content.split('\n'):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent // 4)

        score += max_indent * 2

        # Normalize by content length
        return score / max(len(content), 1) * 1000

# Usage
engine = TrajectoryEngine()
analyzer = CodeComplexityAnalyzer()
engine.register_analyzer(analyzer.analyze_direction)
```

---

## 3. Custom Visual Renderer

### Use Case: Mermaid Diagram Generator

Generate Mermaid diagrams from trajectory segments:

```python
from visual_renderer import VisualRenderer, PreviewFrame, VisualElement
from typing import Dict, Any, List

class MermaidRenderer(VisualRenderer):
    """Renders trajectory as Mermaid flowchart"""

    def render_mermaid_flowchart(self, trajectory_data: Dict[str, Any]) -> str:
        """Generate Mermaid flowchart from trajectory"""
        segments = trajectory_data.get("segments", [])

        if not segments:
            return "graph TD\n    Start[No Data]"

        lines = ["graph TD"]

        for i, segment in enumerate(segments):
            node_id = f"S{i}"
            direction = segment.get("dominant_direction", "uncertain")
            confidence = segment.get("avg_confidence", 0.5)
            duration = segment.get("duration", 0)

            # Node definition with styling
            label = f"{direction.upper()}<br/>conf: {confidence:.2f}<br/>dur: {duration:.1f}s"
            style = self._get_mermaid_style(direction)

            lines.append(f'    {node_id}["{label}"]')
            lines.append(f'    style {node_id} {style}')

            # Connect to previous segment
            if i > 0:
                prev_id = f"S{i-1}"
                lines.append(f'    {prev_id} --> {node_id}')

        return "\n".join(lines)

    def _get_mermaid_style(self, direction: str) -> str:
        """Get Mermaid style for direction"""
        styles = {
            "expanding": "fill:#4CAF50,stroke:#2E7D32,color:#fff",
            "converging": "fill:#2196F3,stroke:#1565C0,color:#fff",
            "pivoting": "fill:#FF9800,stroke:#E65100,color:#fff",
            "stable": "fill:#9E9E9E,stroke:#424242,color:#fff",
            "uncertain": "fill:#9C27B0,stroke:#4A148C,color:#fff"
        }
        return styles.get(direction, styles["uncertain"])

    def render(self, trajectory_data: Dict[str, Any], input_context: Dict[str, Any] = None) -> PreviewFrame:
        """Override render to include Mermaid output"""
        # Call parent render for standard frame
        frame = super().render(trajectory_data, input_context)

        # Add Mermaid diagram to metadata
        mermaid_code = self.render_mermaid_flowchart(trajectory_data)
        frame.metadata["mermaid"] = mermaid_code

        return frame

# Usage
renderer = MermaidRenderer(mode="timeline")
orchestrator = GlimpseOrchestrator()
orchestrator.renderer = renderer
```

---

## 4. Custom Security Validator

### Use Case: Project-Specific Operation Rules

Implement custom security validation for specific operations:

```python
from security_integration import SecurityManager, SecurityContext
from typing import Dict, Any
import re

class ProjectSecurityValidator(SecurityManager):
    """Custom security validator with project-specific rules"""

    def __init__(self, base_path=None, allowed_patterns=None):
        super().__init__(base_path)
        self.allowed_patterns = allowed_patterns or []
        self.blocked_keywords = [
            'rm -rf', 'del /f', 'DROP TABLE', 'DELETE FROM',
            'format', 'mkfs', 'dd if='
        ]

    def validate_operation(self, operation: str) -> bool:
        """Extended validation with pattern matching"""
        # Call parent validation first
        if not super().validate_operation(operation):
            return False

        # Additional project-specific checks
        return self._validate_project_rules(operation)

    def _validate_project_rules(self, operation: str) -> bool:
        """Project-specific validation rules"""
        # Block dangerous keywords
        for keyword in self.blocked_keywords:
            if keyword.lower() in operation.lower():
                LOG.warning(f"Blocked dangerous keyword: {keyword}")
                return False

        # Require pattern match if patterns defined
        if self.allowed_patterns:
            if not any(re.search(pattern, operation) for pattern in self.allowed_patterns):
                LOG.warning(f"Operation doesn't match allowed patterns")
                return False

        return True

    def validate_content_change(self, old_content: str, new_content: str) -> Dict[str, Any]:
        """Validate content changes for sensitive data"""
        result = {"allowed": True, "reasons": []}

        # Check for accidental credential exposure
        credential_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]

        for pattern in credential_patterns:
            if re.search(pattern, new_content, re.IGNORECASE):
                result["allowed"] = False
                result["reasons"].append(f"Possible credential exposure detected")
                break

        return result

# Usage
validator = ProjectSecurityValidator(
    allowed_patterns=[r'\.py$', r'\.md$', r'\.json$']
)
orchestrator = GlimpseOrchestrator()
orchestrator.security = validator
```

---

## 5. Complete Integration Example

### Use Case: AI-Assisted Code Review System

Combine all extensions into a cohesive system:

```python
from pathlib import Path
from realtime_preview import GlimpseOrchestrator, GlimpseConfiguration
from visual_renderer import VisualizationMode

def create_code_review_system(project_path: Path):
    """Create specialized Glimpse system for code review"""

    # Configuration
    config = GlimpseConfiguration(
        visualization_mode=VisualizationMode.TIMELINE,
        enable_security=True,
        enable_predictions=True,
        enable_suggestions=True,
        trajectory_window_size=200,  # Larger window for code
        auto_save_interval=300.0  # Save every 5 minutes
    )

    # Initialize orchestrator
    orchestrator = GlimpseOrchestrator(config=config, base_path=project_path)

    # Replace with custom components
    orchestrator.input_adapter = MarkdownInputAdapter(buffer_size=100)

    # Add custom analyzers
    code_analyzer = CodeComplexityAnalyzer()
    orchestrator.trajectory.register_analyzer(code_analyzer.analyze_direction)

    # Replace renderer
    orchestrator.renderer = MermaidRenderer(mode=VisualizationMode.TIMELINE)

    # Enhanced security
    orchestrator.security = ProjectSecurityValidator(
        base_path=project_path,
        allowed_patterns=[r'\.(py|js|ts|md|json)$']
    )

    # Register event callbacks
    def log_complexity_changes(event_data):
        """Log when code complexity changes significantly"""
        trajectory = event_data.get("trajectory_point", {})
        direction = trajectory.get("direction")

        if direction in ["expanding", "pivoting"]:
            print(f"⚠️ Complexity trend: {direction}")

    orchestrator.register_event_callback(log_complexity_changes)

    return orchestrator

# Usage
system = create_code_review_system(Path("d:/my-project"))
system.start()

# Process code review session
system.process_input(
    action="replace",
    start=0,
    end=0,
    text="def calculate_metrics(data):\n    # Implementation here\n    pass"
)

# Get insights
state = system.get_full_state()
print(f"Current direction: {state['trajectory']['current_direction']}")
print(f"Complexity trend: {state['trajectory']['trajectory_health']}")

# Export session
system.export_session("code_review_session_001")
```

---

## 6. Client-Side Integration

### JavaScript SSE Client

```javascript
class GlimpseClient {
    constructor(serverUrl = 'http://127.0.0.1:8765') {
        this.serverUrl = serverUrl;
        this.eventSource = null;
        this.handlers = {};
    }

    connect() {
        this.eventSource = new EventSource(`${this.serverUrl}/events`);

        this.eventSource.addEventListener('preview', (event) => {
            const data = JSON.parse(event.data);
            this._handlePreview(data);
        });

        this.eventSource.onerror = (error) => {
            console.error('SSE connection error:', error);
        };
    }

    async sendInput(prompt, stage = 'draft') {
        const response = await fetch(`${this.serverUrl}/input`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt, stage })
        });

        return await response.json();
    }

    onPreview(handler) {
        this.handlers.preview = handler;
    }

    _handlePreview(data) {
        if (this.handlers.preview) {
            this.handlers.preview(data);
        }
    }

    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
        }
    }
}

// Usage
const client = new GlimpseClient();

client.onPreview((preview) => {
    console.log('Received preview:', preview.stage);
    console.log('ASCII:', preview.ascii);
    // Update UI with preview
    document.getElementById('preview').textContent = preview.ascii;
});

client.connect();

// Send input
document.getElementById('submitBtn').addEventListener('click', async () => {
    const prompt = document.getElementById('input').value;
    const result = await client.sendInput(prompt, 'draft');
    console.log('Input processed:', result);
});
```

---

## 7. Python Client

```python
import requests
import sseclient
import threading
from typing import Callable, Dict, Any

class GlimpseClient:
    """Python client for Glimpse SSE server"""

    def __init__(self, server_url: str = "http://127.0.0.1:8765"):
        self.server_url = server_url
        self.handlers: Dict[str, Callable] = {}
        self._stream_thread = None
        self._running = False

    def connect(self):
        """Connect to SSE stream"""
        self._running = True
        self._stream_thread = threading.Thread(target=self._listen_stream, daemon=True)
        self._stream_thread.start()

    def _listen_stream(self):
        """Listen to SSE stream in background thread"""
        response = requests.get(f"{self.server_url}/events", stream=True)
        client = sseclient.SSEClient(response)

        for event in client.events():
            if not self._running:
                break

            if event.event == "preview":
                import json
                data = json.loads(event.data)
                self._handle_preview(data)

    def send_input(self, prompt: str, stage: str = "draft") -> Dict[str, Any]:
        """Send input to server"""
        response = requests.post(
            f"{self.server_url}/input",
            json={"prompt": prompt, "stage": stage}
        )
        return response.json()

    def on_preview(self, handler: Callable[[Dict[str, Any]], None]):
        """Register preview handler"""
        self.handlers["preview"] = handler

    def _handle_preview(self, data: Dict[str, Any]):
        """Handle preview event"""
        if "preview" in self.handlers:
            self.handlers["preview"](data)

    def disconnect(self):
        """Disconnect from server"""
        self._running = False

# Usage
client = GlimpseClient()

def handle_preview(preview):
    print(f"Preview ({preview['stage']}):")
    print(preview['ascii'])
    print(f"Job ID: {preview['job_id']}")

client.on_preview(handle_preview)
client.connect()

# Send input
result = client.send_input("def hello():\n    print('world')", stage="draft")
print(f"Input accepted: {result}")

# Keep running
import time
time.sleep(10)

client.disconnect()
```

---

## Testing Extensions

### Unit Test Template

```python
import unittest
from pathlib import Path
from realtime_preview import GlimpseOrchestrator, GlimpseConfiguration

class TestCustomExtensions(unittest.TestCase):

    def setUp(self):
        """Set up test orchestrator"""
        config = GlimpseConfiguration(enable_security=False)
        self.orchestrator = GlimpseOrchestrator(config=config)
        self.orchestrator.start()

    def tearDown(self):
        """Clean up"""
        self.orchestrator.stop()

    def test_custom_analyzer(self):
        """Test custom trajectory analyzer"""
        analyzer = CodeComplexityAnalyzer()
        self.orchestrator.trajectory.register_analyzer(analyzer.analyze_direction)

        # Add complex code
        result = self.orchestrator.process_input(
            action="replace",
            start=0,
            end=0,
            text="if x:\n    if y:\n        if z:\n            pass"
        )

        self.assertIn("trajectory", result)
        direction = result["trajectory"]["current_direction"]
        self.assertIn(direction, ["expanding", "pivoting", "stable"])

    def test_markdown_suggestions(self):
        """Test markdown-aware suggestions"""
        self.orchestrator.input_adapter = MarkdownInputAdapter()

        # Insert heading start
        result = self.orchestrator.process_input(
            action="insert",
            position=0,
            text="# "
        )

        self.assertTrue(result["success"])
        if "suggestions" in result:
            self.assertGreater(len(result["suggestions"]), 0)

if __name__ == "__main__":
    unittest.main()
```

---

## Deployment Checklist

- [ ] Test custom components in isolation
- [ ] Validate security rules with threat scenarios
- [ ] Profile performance under load
- [ ] Configure logging levels appropriately
- [ ] Set up health monitoring
- [ ] Document custom extension APIs
- [ ] Create rollback procedures
- [ ] Prepare client SDK if needed
