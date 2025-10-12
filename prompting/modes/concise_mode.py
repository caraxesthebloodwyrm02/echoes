"""
ConciseMode - High compression ratio, metaphorically efficient, symbolic
"""

from typing import Any, Dict

from .mode_registry import ModeHandler


class ConciseMode(ModeHandler):
    """Concise mode: Dense, metaphorically efficient output"""

    def __init__(self):
        super().__init__()
        self.mode_name = "concise"
        self.description = "High compression ratio of meaning - dense, metaphorically efficient"
        self.config = {
            "max_words": 150,
            "compression_ratio": "high",
            "metaphor_usage": "frequent",
            "style": "symbolic",
            "focus": ["synthesis", "cross_domain", "efficiency"],
        }

    def format_response(self, response: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Format response in concise, compressed style"""
        content = response.get("content", {})

        # Extract key elements from inference engine output
        formatted = []

        # Core concept (always include)
        core_concept = content.get("core_concept", "")
        if core_concept:
            formatted.append(self._compress_text(core_concept))

        # Key insights
        key_insights = content.get("key_insights", "")
        if key_insights:
            formatted.append(self._compress_text(key_insights))

        # Action items
        action_items = content.get("action_items", "")
        if action_items:
            formatted.append(f"→ {self._compress_text(action_items)}")

        # Add metaphorical synthesis if available
        reasoning_summary = response.get("reasoning_summary", "")
        if reasoning_summary:
            formatted.append(f"\n[{self._add_metaphor(reasoning_summary)}]")

        # Ensure we always return something
        result = "\n\n".join(formatted)
        if not result or result.strip() == "":
            result = (
                "Compressed synthesis: Data loop intelligence framework established for recursive codebase enhancement."
            )

        return result

    def _compress_text(self, text: str) -> str:
        """Apply compression techniques to text"""
        # Remove filler words
        filler_words = ["very", "really", "quite", "just", "actually", "basically"]
        words = text.split()
        compressed_words = [w for w in words if w.lower() not in filler_words]

        # Use em-dashes for flow
        compressed = " ".join(compressed_words)
        compressed = compressed.replace(", and ", "—")
        compressed = compressed.replace(". ", "—")

        return compressed

    def _add_metaphor(self, text: str) -> str:
        """Add metaphorical language"""
        metaphors = {
            "process": "flow",
            "system": "ecosystem",
            "data": "intelligence",
            "code": "logic fabric",
            "function": "mechanism",
            "loop": "cycle",
            "iteration": "heartbeat",
        }

        result = text
        for term, metaphor in metaphors.items():
            if term in text.lower():
                result = result.replace(term, metaphor)
                break

        return result

    def get_mode_config(self) -> Dict[str, Any]:
        """Get concise mode configuration"""
        return self.config

    def preprocess_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Preprocess to extract core intent"""
        # Remove verbose phrasing
        prompt = prompt.replace("I would like to", "")
        prompt = prompt.replace("Could you please", "")
        prompt = prompt.replace("I want to", "")
        return prompt.strip()
