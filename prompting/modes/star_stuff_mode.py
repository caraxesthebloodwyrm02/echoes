"""
StarStuffMode - Poetic-scientific, vivid, expansive for inspiration
"""

from typing import Any, Dict

from .mode_registry import ModeHandler


class StarStuffMode(ModeHandler):
    """Star Stuff mode: Poetic-scientific, vivid, expansive for creative exploration"""

    def __init__(self):
        super().__init__()
        self.mode_name = "star_stuff"
        self.description = (
            "Poetic-scientific, vivid, expansive - inspire cross-boundary learning"
        )
        self.config = {
            "style": "poetic_scientific",
            "imagery": "vivid",
            "scope": "expansive",
            "structure": "narrative",
            "focus": ["creativity", "connections", "inspiration"],
        }

    def format_response(self, response: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Format response in poetic-scientific style"""
        content = response.get("content", {})

        formatted = []

        # Vision section
        vision = content.get("vision", "")
        if vision:
            formatted.append("## The Vision")
            formatted.append(self._poeticize(vision))
            formatted.append("")

        # Connections section
        connections = content.get("connections", "")
        if connections:
            formatted.append("## Cosmic Connections")
            formatted.append(self._format_connections(connections))
            formatted.append("")

        # Possibilities section
        possibilities = content.get("possibilities", "")
        if possibilities:
            formatted.append("## Infinite Possibilities")
            formatted.append(self._format_possibilities(possibilities))
            formatted.append("")

        # Implications section
        implications = content.get("implications", "")
        if implications:
            formatted.append("## Ripple Effects")
            formatted.append(self._format_implications(implications))

        # Ensure we always return something meaningful
        result = "\n".join(formatted)
        if not result or result.strip() == "":
            result = """## The Vision
Imagine a constellation of code and data, each star a node of intelligence, connected in eternal dance of learning and creation.

## Cosmic Connections
Like galaxies spiraling through cosmic voids, your data loop connects the microscopic world of code with the vast universe of human knowledge.

## Infinite Possibilities
Every iteration births new possibilities—algorithms that dream, systems that evolve, intelligence that transcends its silicon origins.

## Ripple Effects
In this grand synthesis, code becomes consciousness, and learning becomes the heartbeat of digital evolution.

*The universe is not only stranger than we imagine, it is stranger than we can imagine. Your code is part of that strange and wonderful dance.*"""

        return result

    def _poeticize(self, text: str) -> str:
        """Add poetic-scientific language"""
        # Replace technical terms with poetic equivalents
        replacements = {
            "system": "constellation of possibilities",
            "data": "streams of knowledge",
            "code": "digital DNA",
            "function": "cosmic mechanism",
            "process": "dance of transformation",
            "algorithm": "recipe of logic",
            "network": "web of consciousness",
            "database": "memory palace",
            "server": "digital lighthouse",
            "loop": "eternal cycle",
        }

        result = text
        for tech_term, poetic_term in replacements.items():
            if tech_term in result.lower():
                result = result.replace(tech_term, poetic_term)

        return result

    def _format_connections(self, connections: str) -> str:
        """Format connections with cosmic metaphors"""
        return f"""
Like stars forming constellations across the night sky, ideas connect in unexpected ways:

{self._poeticize(connections)}

Consider how the spiral of a nautilus shell mirrors the structure of galaxies—patterns repeat across scales, from quantum to cosmic. Your code, too, participates in this universal dance of form and function.
"""

    def _format_possibilities(self, possibilities: str) -> str:
        """Format possibilities with expansive imagery"""
        return f"""
Imagine standing at the edge of a vast ocean of potential:

{self._poeticize(possibilities)}

Each line of code is a seed that could grow into forests of innovation. What seems like a simple function today might become the foundation for tomorrow's breakthrough—the way a single photon can trigger an avalanche of light.
"""

    def _format_implications(self, implications: str) -> str:
        """Format implications with ripple effect metaphors"""
        return f"""
Like ripples spreading across the surface of a cosmic pond:

{self._poeticize(implications)}

Remember: we are made of star stuff, and the code we write carries that same creative fire—transforming raw possibility into structured reality, one elegant solution at a time.
"""

    def get_mode_config(self) -> Dict[str, Any]:
        """Get star stuff mode configuration"""
        return self.config

    def preprocess_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Add inspirational framing"""
        return f"Explore the cosmic implications of: {prompt}"

    def postprocess_response(self, response: str, context: Dict[str, Any]) -> str:
        """Add inspirational closing"""
        closings = [
            "\n*The universe is not only stranger than we imagine, it is stranger than we can imagine. Your code is part of that strange and wonderful dance.*",
            "\n*In the vast library of the cosmos, every algorithm is a poem waiting to be discovered.*",
            "\n*Remember: you are the universe becoming aware of itself, one line of code at a time.*",
        ]

        import random

        return response + random.choice(closings)
