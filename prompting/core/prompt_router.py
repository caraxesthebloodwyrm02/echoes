"""
PromptRouter - Core control node that routes input to appropriate mode processor
"""

import re
from enum import Enum
from typing import Any, Dict, Optional


class ModeType(Enum):
    CONCISE = "concise"
    IDE = "ide"
    CONVERSATIONAL = "conversational"
    STAR_STUFF = "star_stuff"
    BUSINESS = "business"
    AUTO = "auto"


class PromptRouter:
    """Routes input prompts to appropriate mode processors based on content analysis"""

    def __init__(self):
        self.mode_patterns = {
            ModeType.CONCISE: [
                r"\b(summarize|compress|brief|dense|minimal)\b",
                r"\b(synthesis|cross-domain|strategy)\b",
                r"\b(quick|fast|efficient)\b",
            ],
            ModeType.IDE: [
                r"\b(code|implement|debug|refactor|architecture)\b",
                r"\b(step-by-step|documentation|technical|setup)\b",
                r"\b(function|class|module|package)\b",
                r"\b(test|testing|unittest|pytest)\b",
            ],
            ModeType.CONVERSATIONAL: [
                r"\b(explain|help|understand|learn|teach)\b",
                r"\b(how|why|what|when|where)\b",
                r"\b(friendly|simple|easy|beginner)\b",
            ],
            ModeType.STAR_STUFF: [
                r"\b(explore|discover|creative|innovative|inspire)\b",
                r"\b(imagine|dream|vision|future|possibility)\b",
                r"\b(cross-boundary|interdisciplinary|breakthrough)\b",
            ],
            ModeType.BUSINESS: [
                r"\b(roi|kpi|metrics|analytics|performance)\b",
                r"\b(strategy|execution|decision|plan|action)\b",
                r"\b(business|commercial|profit|revenue)\b",
                r"\b(data-driven|insights|reports)\b",
            ],
        }

        self.context_keywords = {
            "codebase": r"\b(repository|repo|codebase|project|code)\b",
            "data_loop": r"\b(data.*loop|feedback.*loop|iterative|recursive)\b",
            "web_search": r"\b(search|web|internet|online|community)\b",
            "analysis": r"\b(analyze|analysis|examine|investigate)\b",
        }

    def detect_mode(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> ModeType:
        """
        Detect the most appropriate mode for the given prompt

        Args:
            prompt: Input prompt text
            context: Optional context information

        Returns:
            Detected mode type
        """
        prompt_lower = prompt.lower()
        mode_scores = {}

        # Score each mode based on pattern matching
        for mode, patterns in self.mode_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, prompt_lower))
                score += matches
            mode_scores[mode] = score

        # Apply context-based adjustments
        if context:
            self._adjust_scores_by_context(mode_scores, context, prompt_lower)

        # Return mode with highest score, default to CONVERSATIONAL
        if not any(mode_scores.values()):
            return ModeType.CONVERSATIONAL

        return max(mode_scores, key=mode_scores.get)

    def _adjust_scores_by_context(
        self,
        mode_scores: Dict[ModeType, int],
        context: Dict[str, Any],
        prompt_lower: str,
    ):
        """Adjust mode scores based on context"""

        # If in a code project context, boost IDE mode
        if context.get("project_root") or context.get("current_file"):
            mode_scores[ModeType.IDE] += 2

        # If user has technical background, slightly boost IDE and CONCISE
        if context.get("user_profile", {}).get("technical_level") == "expert":
            mode_scores[ModeType.IDE] += 1
            mode_scores[ModeType.CONCISE] += 1

        # If in business context, boost BUSINESS mode
        if context.get("environment") == "business":
            mode_scores[ModeType.BUSINESS] += 2

        # Check for specific context keywords
        for keyword, pattern in self.context_keywords.items():
            if re.search(pattern, prompt_lower):
                if keyword == "codebase":
                    mode_scores[ModeType.IDE] += 1
                elif keyword == "data_loop":
                    mode_scores[ModeType.CONCISE] += 1
                    mode_scores[ModeType.IDE] += 1

    def route_to_processor(
        self, prompt: str, mode: ModeType, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route prompt to appropriate processor based on mode

        Args:
            prompt: Input prompt
            mode: Detected or specified mode
            context: Optional context

        Returns:
            Routing information for the inference engine
        """
        routing_info = {
            "prompt": prompt,
            "mode": mode,
            "context": context or {},
            "processing_hints": self._get_processing_hints(mode),
            "output_format": self._get_output_format(mode),
        }

        return routing_info

    def _get_processing_hints(self, mode: ModeType) -> Dict[str, Any]:
        """Get processing hints for each mode"""
        hints = {
            ModeType.CONCISE: {
                "compression_ratio": "high",
                "metaphor_usage": "frequent",
                "reasoning_depth": "compressed",
                "focus": "synthesis",
            },
            ModeType.IDE: {
                "precision": "maximum",
                "structure": "step_by_step",
                "documentation": "exhaustive",
                "focus": "implementation",
            },
            ModeType.CONVERSATIONAL: {
                "tone": "friendly",
                "complexity": "simplified",
                "examples": "frequent",
                "focus": "understanding",
            },
            ModeType.STAR_STUFF: {
                "style": "poetic_scientific",
                "imagery": "vivid",
                "scope": "expansive",
                "focus": "inspiration",
            },
            ModeType.BUSINESS: {
                "tone": "decisive",
                "data_focus": "metrics",
                "structure": "executive_summary",
                "focus": "execution",
            },
        }

        return hints.get(mode, {})

    def _get_output_format(self, mode: ModeType) -> Dict[str, Any]:
        """Get expected output format for each mode"""
        formats = {
            ModeType.CONCISE: {
                "max_length": "short",
                "structure": "compressed",
                "sections": ["synthesis"],
            },
            ModeType.IDE: {
                "max_length": "detailed",
                "structure": "hierarchical",
                "sections": ["steps", "code", "tests", "documentation"],
            },
            ModeType.CONVERSATIONAL: {
                "max_length": "medium",
                "structure": "flowing",
                "sections": ["explanation", "examples"],
            },
            ModeType.STAR_STUFF: {
                "max_length": "medium",
                "structure": "narrative",
                "sections": ["vision", "connections", "possibilities"],
            },
            ModeType.BUSINESS: {
                "max_length": "executive",
                "structure": "bullet_points",
                "sections": ["objectives", "metrics", "actions"],
            },
        }

        return formats.get(mode, {})
