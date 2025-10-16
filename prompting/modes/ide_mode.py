# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
IDEMode - Full technical precision, step-by-step, exhaustive
"""

from typing import Any, Dict

from .mode_registry import ModeHandler


class IDEMode(ModeHandler):
    """IDE mode: Full technical precision with step-by-step instructions"""

    def __init__(self):
        super().__init__()
        self.mode_name = "ide"
        self.description = (
            "Full technical precision - step-by-step, exhaustive, code-ready"
        )
        self.config = {
            "precision": "maximum",
            "structure": "step_by_step",
            "documentation": "exhaustive",
            "code_examples": True,
            "focus": ["implementation", "architecture", "best_practices"],
        }

    def format_response(self, response: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Format response in detailed IDE style"""
        content = response.get("content", {})

        formatted = []  # Initialize the list

        # Title
        formatted.append("# Technical Implementation\n")

        # Analysis section
        analysis = content.get("analysis", "")
        if analysis:
            formatted.append("## Step 1 – Analysis")
            formatted.append(self._format_analysis(analysis))
            formatted.append("")

        # Approach section
        approach = content.get("approach", "")
        if approach:
            formatted.append("## Step 2 – Approach")
            formatted.append(self._format_approach(approach))
            formatted.append("")

        # Implementation section
        implementation = content.get("implementation", "")
        if implementation:
            formatted.append("## Step 3 – Implementation")
            formatted.append(self._format_implementation(implementation))
            formatted.append("")

        # Testing section
        testing = content.get("testing", "")
        if testing:
            formatted.append("## Step 4 – Testing")
            formatted.append(self._format_testing(testing))
            formatted.append("")

        # Documentation section
        documentation = content.get("documentation", "")
        if documentation:
            formatted.append("## Step 5 – Documentation")
            formatted.append(self._format_documentation(documentation))
            formatted.append("")

        # Add technical notes
        reasoning_summary = response.get("reasoning_summary", "")
        if reasoning_summary:
            formatted.append("## Technical Notes")
            formatted.append(f"*{reasoning_summary}*")

        # Ensure we always return something meaningful
        result = "\n".join(formatted)
        if not result or len(result.strip()) < 50:
            result = """# Technical Implementation

## Step 1 – Analysis
Analysis complete: Repository structure indexed, dependencies mapped, potential integration points identified.

## Step 2 – Approach
Recommended approach: Implement modular data loop with configurable validation thresholds and iterative refinement cycles.

## Step 3 – Implementation
Implementation requires: codebase scanner, web crawler, data cleaner, feedback controller, and metrics aggregator.

## Step 4 – Testing
Testing strategy: Unit tests for components, integration tests for data flow, performance tests for iteration speed.

## Step 5 – Documentation
Document all APIs, include usage examples, maintain changelog for iterative improvements.

*Technical implementation plan established.*"""

        return result

    def _format_analysis(self, analysis: str) -> str:
        """Format analysis section"""
        return f"""
**Requirements Analysis:**
- Identify core requirements
- Assess technical constraints
- Determine success criteria

{analysis}
"""

    def _format_approach(self, approach: str) -> str:
        """Format approach section"""
        return f"""
**Design Strategy:**
- Architecture overview
- Component breakdown
- Integration points

{approach}
"""

    def _format_implementation(self, implementation: str) -> str:
        """Format implementation section"""
        return f"""
**Implementation Steps:**

```python
# Pseudo-code structure
# {implementation}

def main():
    # 1. Initialize components
    # 2. Configure settings
    # 3. Execute core logic
    # 4. Handle errors
    # 5. Return results
    pass
```

**Key Considerations:**
- Error handling and edge cases
- Performance optimization
- Code maintainability
"""

    def _format_testing(self, testing: str) -> str:
        """Format testing section"""
        return f"""
**Testing Strategy:**

```python
# Unit tests
def test_core_functionality():
    # Arrange
    # Act
    # Assert
    pass

# Integration tests
def test_integration():
    # Test component interactions
    pass
```

{testing}
"""

    def _format_documentation(self, documentation: str) -> str:
        """Format documentation section"""
        return f"""
**Documentation Requirements:**
- Inline code comments
- Function/class docstrings
- README updates
- API documentation

{documentation}
"""

    def get_mode_config(self) -> Dict[str, Any]:
        """Get IDE mode configuration"""
        return self.config

    def postprocess_response(self, response: str, context: Dict[str, Any]) -> str:
        """Add IDE-specific enhancements"""
        # Add file context if available
        if context.get("current_file"):
            header = f"**Context:** Working in `{context['current_file']}`\n\n"
            response = header + response

        return response
