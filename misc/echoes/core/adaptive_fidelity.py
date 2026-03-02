"""
Adaptive Fidelity System for Unified Input Comprehension
========================================================

Dynamically adjusts processing detail level based on context, task complexity,
and resource availability. Implements intelligent zooming in/out of processing
depth to optimize performance while maintaining quality.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class FidelityLevel(Enum):
    """Processing fidelity levels from coarse to fine-grained."""

    SURFACE = "surface"  # Basic recognition, minimal detail
    STANDARD = "standard"  # Balanced detail level
    DETAILED = "detailed"  # High detail, comprehensive analysis
    EXHAUSTIVE = "exhaustive"  # Maximum detail, full analysis


class ProcessingContext(Enum):
    """Context types that influence fidelity decisions."""

    CONVERSATION = "conversation"
    ANALYSIS = "analysis"
    CREATION = "creation"
    VERIFICATION = "verification"
    SEARCH = "search"
    EXECUTION = "execution"


@dataclass
class FidelityMetrics:
    """Metrics used to determine optimal fidelity level."""

    complexity_score: float = 0.0  # 0-1 scale
    time_pressure: float = 0.0  # 0-1 scale (higher = more urgent)
    resource_availability: float = 1.0  # 0-1 scale (higher = more resources)
    accuracy_requirement: float = 0.5  # 0-1 scale (higher = more accuracy needed)
    user_preference: float = 0.5  # 0-1 scale (user's detail preference)


class AdaptiveFidelityController:
    """
    Intelligent controller that dynamically adjusts processing fidelity
    based on multiple contextual factors.
    """

    def __init__(self):
        self.fidelity_weights = {
            "complexity": 0.3,
            "time_pressure": 0.2,
            "resource_availability": 0.15,
            "accuracy_requirement": 0.25,
            "user_preference": 0.1,
        }

        # Context-specific fidelity mappings
        self.context_mappings = {
            ProcessingContext.CONVERSATION: {
                "default_level": FidelityLevel.STANDARD,
                "complexity_threshold": 0.6,
                "time_factor": 1.2,  # Conversational responses need to be quick
            },
            ProcessingContext.ANALYSIS: {
                "default_level": FidelityLevel.DETAILED,
                "complexity_threshold": 0.4,
                "time_factor": 0.8,  # Analysis can take longer
            },
            ProcessingContext.CREATION: {
                "default_level": FidelityLevel.DETAILED,
                "complexity_threshold": 0.5,
                "time_factor": 0.9,
            },
            ProcessingContext.VERIFICATION: {
                "default_level": FidelityLevel.EXHAUSTIVE,
                "complexity_threshold": 0.3,
                "time_factor": 0.7,  # Verification needs accuracy over speed
            },
            ProcessingContext.SEARCH: {
                "default_level": FidelityLevel.STANDARD,
                "complexity_threshold": 0.7,
                "time_factor": 1.1,  # Search needs to be responsive
            },
            ProcessingContext.EXECUTION: {
                "default_level": FidelityLevel.STANDARD,
                "complexity_threshold": 0.5,
                "time_factor": 1.0,
            },
        }

    def assess_complexity(self, input_data: dict[str, Any]) -> float:
        """
        Assess the complexity of input data on a 0-1 scale.

        Factors considered:
        - Input length/size
        - Modality diversity (text, image, audio)
        - Semantic complexity
        - Ambiguity level
        """
        complexity = 0.0

        # Length/size factor
        if "text" in input_data:
            text_length = len(input_data["text"])
            # Normalize text length (0-1000 chars = 0-0.5 complexity)
            length_score = min(text_length / 2000, 0.5)
            complexity += length_score * 0.4

        # Modality diversity factor
        modalities = []
        if "text" in input_data:
            modalities.append("text")
        if "image" in input_data:
            modalities.append("image")
        if "audio" in input_data:
            modalities.append("audio")
        if "video" in input_data:
            modalities.append("video")

        modality_score = min(len(modalities) / 4, 1.0) * 0.3
        complexity += modality_score

        # Semantic complexity (estimated by word diversity)
        if "text" in input_data:
            words = input_data["text"].lower().split()
            unique_words = len(set(words))
            diversity_ratio = unique_words / len(words) if words else 0
            semantic_score = min(diversity_ratio * 2, 1.0) * 0.3
            complexity += semantic_score

        return min(complexity, 1.0)

    def assess_time_pressure(
        self, context: ProcessingContext, historical_response_times: list[float] = None
    ) -> float:
        """
        Assess time pressure based on context and historical patterns.
        """
        base_pressure = {
            ProcessingContext.CONVERSATION: 0.8,  # High pressure for real-time chat
            ProcessingContext.ANALYSIS: 0.3,  # Lower pressure for analysis
            ProcessingContext.CREATION: 0.4,
            ProcessingContext.VERIFICATION: 0.2,  # Verification can take time
            ProcessingContext.SEARCH: 0.7,  # Search should be quick
            ProcessingContext.EXECUTION: 0.6,
        }.get(context, 0.5)

        # Adjust based on recent response times if available
        if historical_response_times and len(historical_response_times) > 5:
            avg_time = np.mean(historical_response_times[-5:])
            if avg_time > 10:  # If responses are slow, increase pressure
                base_pressure = min(base_pressure + 0.2, 1.0)

        return base_pressure

    def calculate_optimal_fidelity(
        self, metrics: FidelityMetrics, context: ProcessingContext
    ) -> FidelityLevel:
        """
        Calculate the optimal fidelity level based on all factors.
        """
        # Get context-specific settings
        ctx_settings = self.context_mappings.get(
            context, self.context_mappings[ProcessingContext.CONVERSATION]
        )

        # Calculate weighted fidelity score
        fidelity_score = (
            metrics.complexity_score * self.fidelity_weights["complexity"]
            + metrics.time_pressure * self.fidelity_weights["time_pressure"]
            + (1 - metrics.resource_availability)
            * self.fidelity_weights["resource_availability"]
            + metrics.accuracy_requirement
            * self.fidelity_weights["accuracy_requirement"]
            + metrics.user_preference * self.fidelity_weights["user_preference"]
        )

        # Apply context-specific adjustments
        fidelity_score *= ctx_settings["time_factor"]

        # Adjust based on complexity threshold
        if metrics.complexity_score > ctx_settings["complexity_threshold"]:
            fidelity_score += 0.2  # Boost fidelity for complex inputs

        # Clamp to valid range
        fidelity_score = max(0.0, min(1.0, fidelity_score))

        # Map score to fidelity level
        if fidelity_score < 0.25:
            return FidelityLevel.SURFACE
        elif fidelity_score < 0.5:
            return FidelityLevel.STANDARD
        elif fidelity_score < 0.75:
            return FidelityLevel.DETAILED
        else:
            return FidelityLevel.EXHAUSTIVE

    def get_processing_parameters(
        self, fidelity_level: FidelityLevel, modality: str
    ) -> dict[str, Any]:
        """
        Get processing parameters based on fidelity level and modality.
        """
        base_params = {
            FidelityLevel.SURFACE: {
                "max_tokens": 100,
                "detail_level": "minimal",
                "analysis_depth": "basic",
                "confidence_threshold": 0.6,
            },
            FidelityLevel.STANDARD: {
                "max_tokens": 300,
                "detail_level": "moderate",
                "analysis_depth": "standard",
                "confidence_threshold": 0.75,
            },
            FidelityLevel.DETAILED: {
                "max_tokens": 600,
                "detail_level": "comprehensive",
                "analysis_depth": "detailed",
                "confidence_threshold": 0.85,
            },
            FidelityLevel.EXHAUSTIVE: {
                "max_tokens": 1200,
                "detail_level": "exhaustive",
                "analysis_depth": "maximum",
                "confidence_threshold": 0.95,
            },
        }

        params = base_params[fidelity_level].copy()

        # Modality-specific adjustments
        if modality == "image":
            if fidelity_level == FidelityLevel.SURFACE:
                params["resolution"] = "low"
                params["analysis_type"] = "basic_caption"
            elif fidelity_level == FidelityLevel.STANDARD:
                params["resolution"] = "medium"
                params["analysis_type"] = "detailed_description"
            elif fidelity_level == FidelityLevel.DETAILED:
                params["resolution"] = "high"
                params["analysis_type"] = "comprehensive_analysis"
            else:  # EXHAUSTIVE
                params["resolution"] = "maximum"
                params["analysis_type"] = "forensic_analysis"

        elif modality == "audio":
            if fidelity_level == FidelityLevel.SURFACE:
                params["transcription_detail"] = "basic"
            elif fidelity_level == FidelityLevel.STANDARD:
                params["transcription_detail"] = "standard"
            elif fidelity_level == FidelityLevel.DETAILED:
                params["transcription_detail"] = "detailed"
            else:  # EXHAUSTIVE
                params["transcription_detail"] = "verbatim"

        elif modality == "text":
            if fidelity_level == FidelityLevel.SURFACE:
                params["processing_mode"] = "summarize"
            elif fidelity_level == FidelityLevel.STANDARD:
                params["processing_mode"] = "analyze"
            elif fidelity_level == FidelityLevel.DETAILED:
                params["processing_mode"] = "comprehensive"
            else:  # EXHAUSTIVE
                params["processing_mode"] = "exhaustive"

        return params

    def adapt_processing_plan(
        self,
        input_data: dict[str, Any],
        context: ProcessingContext,
        user_preferences: dict[str, Any] = None,
        historical_performance: list[dict] = None,
    ) -> dict[str, Any]:
        """
        Create an adaptive processing plan based on all contextual factors.
        """
        # Assess input complexity
        complexity = self.assess_complexity(input_data)

        # Assess time pressure
        time_pressure = self.assess_time_pressure(context)

        # Determine resource availability (simplified)
        resource_availability = 0.8  # Could be based on system load

        # Determine accuracy requirements based on context
        accuracy_req = {
            ProcessingContext.VERIFICATION: 0.9,
            ProcessingContext.ANALYSIS: 0.8,
            ProcessingContext.CREATION: 0.7,
            ProcessingContext.CONVERSATION: 0.6,
            ProcessingContext.SEARCH: 0.6,
            ProcessingContext.EXECUTION: 0.7,
        }.get(context, 0.7)

        # User preference (default to balanced)
        user_pref = (
            user_preferences.get("detail_level", 0.5) if user_preferences else 0.5
        )

        # Create metrics object
        metrics = FidelityMetrics(
            complexity_score=complexity,
            time_pressure=time_pressure,
            resource_availability=resource_availability,
            accuracy_requirement=accuracy_req,
            user_preference=user_pref,
        )

        # Calculate optimal fidelity
        optimal_fidelity = self.calculate_optimal_fidelity(metrics, context)

        # Get modality-specific parameters
        modality = self._detect_primary_modality(input_data)
        processing_params = self.get_processing_parameters(optimal_fidelity, modality)

        return {
            "fidelity_level": optimal_fidelity.value,
            "complexity_score": complexity,
            "processing_parameters": processing_params,
            "modality": modality,
            "context": context.value,
            "metrics": {
                "complexity": complexity,
                "time_pressure": time_pressure,
                "resource_availability": resource_availability,
                "accuracy_requirement": accuracy_req,
                "user_preference": user_pref,
            },
        }

    def _detect_primary_modality(self, input_data: dict[str, Any]) -> str:
        """Detect the primary modality of the input data."""
        if "image" in input_data or "image_path" in input_data:
            return "image"
        elif "audio" in input_data or "audio_path" in input_data:
            return "audio"
        elif "video" in input_data or "video_path" in input_data:
            return "video"
        else:
            return "text"
