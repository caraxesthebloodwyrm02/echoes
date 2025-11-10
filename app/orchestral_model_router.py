"""
Orchestral Enhanced Model Router for EchoesAssistantV2
Integrates spatial and temporal processing with intelligent model selection
"""

import logging
import re
import time
from collections import defaultdict
from typing import Any, Dict, List

# Import orchestral components
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

try:
    from orchestral_strategy import OrchestralConductor, OrchestralConfig
    from template_process import TemplateProcessor
except ImportError:
    OrchestralConductor = None
    TemplateProcessor = None

logger = logging.getLogger(__name__)


class OrchestralModelRouter:
    """
    Enhanced model router with orchestral capabilities.
    Routes requests to appropriate models while applying spatial/temporal optimization.
    """

    def __init__(self):
        """Initialize the orchestral model router."""
        self.default_model = "gpt-4o-mini"
        self.complexity_threshold = 0.7
        self.web_search_indicators = [
            "search",
            "find",
            "lookup",
            "research",
            "what is",
            "who is",
            "when did",
            "where is",
            "why does",
            "how does",
        ]

        # Orchestral components
        if OrchestralConductor and TemplateProcessor:
            self.orchestral_config = OrchestralConfig(
                echo_core_path=str(Path(__file__).parent.parent),
                reverb_module_path=str(Path(__file__).parent.parent.parent / "Reverb"),
                delay_module_path=str(Path(__file__).parent.parent.parent / "Delay"),
                routing_connector_path=str(
                    Path(__file__).parent.parent.parent / "Routing"
                ),
                arcade_platform_path=str(
                    Path(__file__).parent.parent.parent / "Arcade"
                ),
            )
            self.conductor = OrchestralConductor(self.orchestral_config)
            self.template_processor = TemplateProcessor()
            self.orchestral_enabled = True
        else:
            self.conductor = None
            self.template_processor = None
            self.orchestral_enabled = False

        # Performance tracking
        self.performance_metrics = defaultdict(list)
        self.routing_decisions = defaultdict(int)

    def route_request(
        self, prompt: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Route request to optimal model with orchestral enhancement.

        Args:
            prompt: The input prompt
            context: Additional context for routing decision

        Returns:
            Routing decision with model selection and optimizations
        """
        start_time = time.time()
        context = context or {}

        # Analyze prompt characteristics
        complexity = self._calculate_complexity(prompt)
        needs_web_search = self._needs_web_search(prompt)
        tool_requirements = self._analyze_tool_requirements(prompt)

        # Base model selection
        selected_model = self._select_base_model(
            complexity, needs_web_search, tool_requirements
        )

        # Apply orchestral enhancement if available
        if self.orchestral_enabled:
            routing_result = self._apply_orchestral_routing(
                prompt, selected_model, complexity, context
            )
        else:
            routing_result = {
                "selected_model": selected_model,
                "complexity": complexity,
                "needs_web_search": needs_web_search,
                "tool_requirements": tool_requirements,
                "orchestral_enhanced": False,
            }

        # Track performance
        processing_time = time.time() - start_time
        self.performance_metrics["routing_time"].append(processing_time)
        self.routing_decisions[selected_model] += 1

        routing_result["routing_time"] = processing_time
        routing_result["timestamp"] = time.time()

        logger.info(
            f"Routed to {selected_model} in {processing_time:.3f}s (orchestral: {routing_result.get('orchestral_enhanced', False)})"
        )

        return routing_result

    def _calculate_complexity(self, prompt: str) -> float:
        """Calculate prompt complexity score."""
        factors = {
            "length": min(len(prompt) / 1000, 1.0),
            "questions": prompt.count("?") / 10,
            "technical_terms": len(
                re.findall(
                    r"\b(API|algorithm|function|class|method)\b", prompt, re.IGNORECASE
                )
            )
            / 5,
            "complex_sentences": len(
                re.findall(
                    r"\b(how|why|explain|analyze|compare)\b", prompt, re.IGNORECASE
                )
            )
            / 5,
        }

        complexity = sum(factors.values()) / len(factors)
        return min(complexity, 1.0)

    def _needs_web_search(self, prompt: str) -> bool:
        """Determine if prompt requires web search."""
        prompt_lower = prompt.lower()
        return any(
            indicator in prompt_lower for indicator in self.web_search_indicators
        )

    def _analyze_tool_requirements(self, prompt: str) -> List[str]:
        """Analyze what tools are needed for the prompt."""
        tools = []
        prompt_lower = prompt.lower()

        tool_indicators = {
            "code_execution": ["run", "execute", "compile", "test"],
            "file_operations": ["file", "read", "write", "save", "open"],
            "web_search": ["search", "find", "lookup", "research"],
            "data_analysis": ["analyze", "process", "calculate", "statistics"],
        }

        for tool, indicators in tool_indicators.items():
            if any(indicator in prompt_lower for indicator in indicators):
                tools.append(tool)

        return tools

    def _select_base_model(
        self, complexity: float, needs_web_search: bool, tools: List[str]
    ) -> str:
        """Select base model based on requirements."""
        if complexity > self.complexity_threshold or needs_web_search or len(tools) > 2:
            return "gpt-4o"
        elif len(tools) > 0 or complexity > 0.5:
            return "gpt-4o-mini"
        else:
            return self.default_model

    def _apply_orchestral_routing(
        self, prompt: str, base_model: str, complexity: float, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply orchestral enhancement to routing decision."""

        # Determine optimal processing pattern
        if self._needs_web_search(prompt):
            pattern = "web_search"
        elif complexity > 0.7:
            pattern = "summarize_results"
        elif "status" in prompt.lower():
            pattern = "status_monitoring"
        else:
            pattern = "list_providers"

        # Apply template processing
        template_result = self.template_processor.process(
            pattern,
            {"query": prompt, "complexity": complexity, "base_model": base_model},
        )

        # Enhance with spatial/temporal optimization
        enhanced_result = template_result.copy()
        enhanced_result.update(
            {
                "selected_model": base_model,
                "complexity": complexity,
                "orchestral_pattern": pattern,
                "spatial_enhancement": True,
                "temporal_optimization": True,
                "orchestral_enhanced": True,
            }
        )

        return enhanced_result

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing performance statistics."""
        stats = {
            "total_routes": sum(self.routing_decisions.values()),
            "model_distribution": dict(self.routing_decisions),
            "average_routing_time": (
                sum(self.performance_metrics["routing_time"])
                / len(self.performance_metrics["routing_time"])
                if self.performance_metrics["routing_time"]
                else 0
            ),
            "orchestral_enabled": self.orchestral_enabled,
        }

        if self.orchestral_enabled:
            stats["orchestral_capabilities"] = [
                "spatial_enhancement",
                "temporal_optimization",
                "pattern_routing",
            ]

        return stats

    def reset_statistics(self):
        """Reset routing statistics."""
        self.performance_metrics.clear()
        self.routing_decisions.clear()


# Global instance
orchestral_router = OrchestralModelRouter()


def route_request_with_orchestral(
    prompt: str, context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Convenience function for routing with orchestral enhancement."""
    return orchestral_router.route_request(prompt, context)


def get_orchestral_routing_status() -> Dict[str, Any]:
    """Get current orchestral routing status."""
    return orchestral_router.get_routing_statistics()


__all__ = [
    "OrchestralModelRouter",
    "route_request_with_orchestral",
    "get_orchestral_routing_status",
]
