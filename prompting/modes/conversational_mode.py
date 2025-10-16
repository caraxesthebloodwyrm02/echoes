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
ConversationalMode - Natural, flowing, simplified for understanding
"""

from typing import Any, Dict

from .mode_registry import ModeHandler


class ConversationalMode(ModeHandler):
    """Conversational mode: Natural, friendly, easy to understand"""

    def __init__(self):
        super().__init__()
        self.mode_name = "conversational"
        self.description = "Natural, flowing, simplified - friendly and discussion-like"
        self.config = {
            "tone": "friendly",
            "complexity": "simplified",
            "examples": "frequent",
            "structure": "flowing",
            "focus": ["understanding", "clarity", "relatability"],
        }

    def format_response(self, response: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Format response in conversational style"""
        content = response.get("content", {})

        formatted = []

        # Start with context setting
        context_text = content.get("context", "")
        if context_text:
            formatted.append(self._format_context(context_text))
            formatted.append("")

        # Main explanation
        explanation = content.get("explanation", "")
        if explanation:
            formatted.append(self._format_explanation(explanation))
            formatted.append("")

        # Add examples
        examples = content.get("examples", "")
        if examples:
            formatted.append(self._format_examples(examples))
            formatted.append("")

        # Summary
        summary = content.get("summary", "")
        if summary:
            formatted.append(self._format_summary(summary))

        # Ensure we always return something meaningful
        result = "\n".join(formatted)
        if not result or result.strip() == "":
            result = """I understand you want to create a smart data loop that learns from your codebase and the web. Basically, it's like giving your code a memory that gets better each time it runs—scanning files, finding patterns, and learning from online resources.

Think of it like how Spotify learns your music taste or how Netflix recommends shows. Your code would learn what works best for your project.

This sounds like a really powerful way to make your development process smarter over time! Let me know if you'd like me to explain any part in more detail."""

        return result

    def _format_context(self, context_text: str) -> str:
        """Format context in conversational style"""
        return f"So, let me help you understand this. {context_text}"

    def _format_explanation(self, explanation: str) -> str:
        """Format explanation with conversational flow"""
        # Add conversational connectors
        explanation = explanation.replace(". ", ". Now, ")
        explanation = explanation.replace("However,", "But here's the thing,")
        explanation = explanation.replace("Therefore,", "So what this means is,")

        return explanation

    def _format_examples(self, examples: str) -> str:
        """Format examples in relatable way"""
        return f"""
**Here's a simple example to make this clearer:**

{examples}

Think of it like this - it's similar to how you might organize your files on your computer. You want everything in the right place so you can find it easily later.
"""

    def _format_summary(self, summary: str) -> str:
        """Format summary conversationally"""
        return f"""
**To wrap this up:** {summary}

Does this make sense? Feel free to ask if you'd like me to explain any part in more detail!
"""

    def get_mode_config(self) -> Dict[str, Any]:
        """Get conversational mode configuration"""
        return self.config

    def preprocess_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Add conversational context"""
        # Check for question words to adjust tone
        question_starters = ["how", "what", "why", "when", "where", "can you"]

        if any(prompt.lower().startswith(q) for q in question_starters):
            return f"Help me understand: {prompt}"

        return prompt

    def postprocess_response(self, response: str, context: Dict[str, Any]) -> str:
        """Add conversational polish"""
        # Add encouraging closing if not already present
        if not any(
            phrase in response.lower()
            for phrase in ["feel free", "let me know", "questions"]
        ):
            response += "\n\nLet me know if you have any questions about this!"

        return response
