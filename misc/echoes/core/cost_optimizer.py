# echoes/core/cost_optimizer.py
"""
Cost optimization module for the Echoes AI Assistant.
Provides smart model routing and usage analytics for OpenAI API cost optimization.
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class CostOptimizer:
    """Smart model router and cost optimizer for OpenAI API calls."""

    def __init__(self):
        # Model pricing per million tokens (as of 2024)
        self.model_pricing = {
            "gpt-4o": {
                "input": 5.00,  # $5 per million input tokens
                "output": 15.00,  # $15 per million output tokens
                "capabilities": ["text", "vision", "tools", "complex_reasoning"],
            },
            "gpt-4o-mini": {
                "input": 0.15,  # $0.15 per million input tokens
                "output": 0.60,  # $0.60 per million output tokens
                "capabilities": ["text", "vision", "tools", "basic_reasoning"],
            },
            "gpt-4-turbo": {
                "input": 10.00,  # $10 per million input tokens
                "output": 30.00,  # $30 per million output tokens
                "capabilities": ["text", "vision", "tools", "complex_reasoning"],
            },
            "gpt-4": {
                "input": 30.00,  # $30 per million input tokens
                "output": 60.00,  # $60 per million output tokens
                "capabilities": ["text", "vision", "tools", "complex_reasoning"],
            },
            "gpt-3.5-turbo": {
                "input": 0.50,  # $0.50 per million input tokens
                "output": 1.50,  # $1.50 per million output tokens
                "capabilities": ["text", "basic_tools"],
            },
        }

        # Add multimodal processing costs
        self.model_pricing.update(
            {
                "whisper-1": {
                    "cost_per_minute": 0.006,  # $0.006 per minute
                    "cost_per_second": 0.0001,  # $0.0001 per second
                },
                "gpt-4o-vision": {
                    "input": 5.00,  # Same as GPT-4o for text
                    "output": 15.00,
                    "image_cost_low": 0.001275,  # per 512x512 low detail
                    "image_cost_high": 0.00255,  # per 512x512 high detail
                },
            }
        )

        # Usage tracking
        self.usage_stats = {"total_tokens": 0, "total_cost": 0.0, "requests": 0, "model_usage": {}, "daily_stats": {}}

        # Cost alerts
        self.cost_alerts = {
            "daily_limit": 10.0,  # $10 per day
            "monthly_limit": 100.0,  # $100 per month
            "alert_threshold": 0.8,  # Alert at 80% of limit
        }

    def select_optimal_model(
        self,
        task_description: str,
        context_length: int = 0,
        requires_vision: bool = False,
        requires_tools: bool = False,
    ) -> str:
        """
        Select the most cost-effective model for a given task.

        Args:
            task_description: Description of the task
            context_length: Length of conversation context in tokens
            requires_vision: Whether vision capabilities are needed
            requires_tools: Whether tool calling is needed

        Returns:
            Optimal model name
        """

        # Analyze task complexity
        task_complexity = self._analyze_task_complexity(task_description)

        # Determine required capabilities
        required_caps = []
        if requires_vision:
            required_caps.append("vision")
        if requires_tools:
            required_caps.append("tools")

        if task_complexity == "simple":
            # Use cheapest model that can handle basic tasks
            if not requires_vision and not requires_tools:
                return "gpt-4o-mini"  # Cheapest for simple text tasks
            elif requires_vision:
                return "gpt-4o"  # Vision requires more capable models
            else:
                return "gpt-4o-mini"

        elif task_complexity == "medium":
            # Use balanced model for moderate complexity
            if requires_vision or context_length > 5000:
                return "gpt-4o"  # Better for longer contexts or vision
            else:
                return "gpt-4o-mini"  # Still cost-effective for medium tasks

        else:  # complex
            # Use most capable model for complex tasks
            return "gpt-4o"  # Best balance of cost and capability

    def _analyze_task_complexity(self, task_description: str) -> str:
        """Analyze task complexity based on description."""
        task_lower = task_description.lower()

        # Simple tasks
        simple_keywords = ["hello", "hi", "thanks", "goodbye", "simple", "basic", "quick"]
        if any(keyword in task_lower for keyword in simple_keywords):
            return "simple"

        # Complex tasks
        complex_keywords = [
            "analyze",
            "design",
            "architecture",
            "complex",
            "research",
            "implement",
            "code",
            "debug",
            "optimize",
            "refactor",
        ]
        if any(keyword in task_lower for keyword in complex_keywords):
            return "complex"

        # Default to medium
        return "medium"

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int = 0) -> float:
        """Estimate cost for a given model and token usage."""
        if model not in self.model_pricing:
            return 0.0

        pricing = self.model_pricing[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def track_usage(self, model: str, input_tokens: int, output_tokens: int, cost: Optional[float] = None) -> None:
        """Track API usage and costs."""
        if cost is None:
            cost = self.estimate_cost(model, input_tokens, output_tokens)

        # Update totals
        self.usage_stats["total_tokens"] += input_tokens + output_tokens
        self.usage_stats["total_cost"] += cost
        self.usage_stats["requests"] += 1

        # Update model-specific stats
        if model not in self.usage_stats["model_usage"]:
            self.usage_stats["model_usage"][model] = {"requests": 0, "tokens": 0, "cost": 0.0}

        self.usage_stats["model_usage"][model]["requests"] += 1
        self.usage_stats["model_usage"][model]["tokens"] += input_tokens + output_tokens
        self.usage_stats["model_usage"][model]["cost"] += cost

        # Daily stats
        today = datetime.now(timezone.utc).date().isoformat()
        if today not in self.usage_stats["daily_stats"]:
            self.usage_stats["daily_stats"][today] = {"cost": 0.0, "tokens": 0, "requests": 0}

        self.usage_stats["daily_stats"][today]["cost"] += cost
        self.usage_stats["daily_stats"][today]["tokens"] += input_tokens + output_tokens
        self.usage_stats["daily_stats"][today]["requests"] += 1

    def check_cost_alerts(self) -> List[str]:
        """Check if any cost alerts should be triggered."""
        alerts = []
        today = datetime.now(timezone.utc).date().isoformat()

        # Daily cost alert
        daily_cost = self.usage_stats["daily_stats"].get(today, {}).get("cost", 0.0)
        if daily_cost >= self.cost_alerts["daily_limit"] * self.cost_alerts["alert_threshold"]:
            alerts.append(f"⚠️ Daily cost alert: ${daily_cost:.2f} of ${self.cost_alerts['daily_limit']:.2f} limit")

        # Monthly cost projection
        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        monthly_cost = sum(
            day_stats.get("cost", 0.0)
            for day_key, day_stats in self.usage_stats["daily_stats"].items()
            if day_key.startswith(current_month)
        )

        days_in_month = 30  # Approximate
        projected_monthly = (
            monthly_cost
            / max(1, len([k for k in self.usage_stats["daily_stats"].keys() if k.startswith(current_month)]))
        ) * days_in_month

        if projected_monthly >= self.cost_alerts["monthly_limit"] * self.cost_alerts["alert_threshold"]:
            alerts.append(
                f"⚠️ Monthly cost projection: ~${projected_monthly:.2f} of ${self.cost_alerts['monthly_limit']:.2f} limit"
            )

        return alerts

    def get_usage_report(self) -> Dict[str, Any]:
        """Generate comprehensive usage report."""
        report = {
            "total_stats": self.usage_stats.copy(),
            "cost_savings_potential": self._calculate_savings_potential(),
            "model_efficiency": self._analyze_model_efficiency(),
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _calculate_savings_potential(self) -> Dict[str, Any]:
        """Calculate potential cost savings."""
        # Analyze current model usage and suggest optimizations
        total_cost = self.usage_stats["total_cost"]
        potential_savings = 0.0

        # If using expensive models for simple tasks, calculate savings
        for model, stats in self.usage_stats["model_usage"].items():
            if model in ["gpt-4", "gpt-4-turbo"]:
                # Could potentially use GPT-4o instead (2-3x savings)
                potential_savings += stats["cost"] * 0.7  # 70% savings estimate

        return {
            "current_cost": total_cost,
            "potential_savings": potential_savings,
            "optimized_cost": total_cost - potential_savings,
            "savings_percentage": (potential_savings / max(0.01, total_cost)) * 100,
        }

    def _analyze_model_efficiency(self) -> Dict[str, Any]:
        """Analyze which models are most cost-effective."""
        efficiency = {}

        for model, stats in self.usage_stats["model_usage"].items():
            if stats["requests"] > 0:
                avg_cost_per_request = stats["cost"] / stats["requests"]
                avg_tokens_per_request = stats["tokens"] / stats["requests"]

                efficiency[model] = {
                    "avg_cost_per_request": avg_cost_per_request,
                    "avg_tokens_per_request": avg_tokens_per_request,
                    "total_cost": stats["cost"],
                    "total_requests": stats["requests"],
                }

        return efficiency

    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []

        # Check for expensive model usage
        expensive_models = ["gpt-4", "gpt-4-turbo"]
        for model in expensive_models:
            if model in self.usage_stats["model_usage"]:
                usage = self.usage_stats["model_usage"][model]
                if usage["requests"] > 10:  # Used more than 10 times
                    recommendations.append(f"Consider switching from {model} to GPT-4o for better cost-efficiency")

        # Check for high daily costs
        today = datetime.now(timezone.utc).date().isoformat()
        daily_cost = self.usage_stats["daily_stats"].get(today, {}).get("cost", 0.0)
        if daily_cost > 5.0:
            recommendations.append(
                "High daily usage detected. Consider implementing usage limits or switching to cheaper models for routine tasks"
            )

        # Check for inefficient token usage
        total_tokens = self.usage_stats["total_tokens"]
        total_requests = self.usage_stats["requests"]
        if total_requests > 0:
            avg_tokens_per_request = total_tokens / total_requests
            if avg_tokens_per_request > 2000:
                recommendations.append(
                    "High token usage per request. Consider optimizing prompts or implementing context compression"
                )

    def track_multimodal_usage(
        self,
        modality: str,
        duration_seconds: float = 0,
        tokens_used: int = 0,
        image_count: int = 0,
        detail_level: str = "low",
    ) -> float:
        """
        Track multimodal processing usage and return cost.

        Args:
            modality: 'audio' or 'image'
            duration_seconds: Audio duration in seconds
            tokens_used: Text tokens used for analysis
            image_count: Number of images processed
            detail_level: 'low' or 'high' for images

        Returns:
            Total cost for the operation
        """
        total_cost = 0.0

        if modality == "audio":
            # Whisper pricing: $0.006 per minute
            duration_minutes = duration_seconds / 60
            total_cost = duration_minutes * self.model_pricing["whisper-1"]["cost_per_minute"]
            self.track_usage("whisper-1", 0, 0, total_cost)

        elif modality == "image":
            # GPT-4o Vision pricing
            # Base text tokens cost
            text_cost = self.estimate_cost("gpt-4o", 0, tokens_used)

            # Image processing cost
            image_cost_per_unit = self.model_pricing["gpt-4o-vision"][f"image_cost_{detail_level}"]
            image_cost = image_count * image_cost_per_unit

            total_cost = text_cost + image_cost
            self.track_usage("gpt-4o-vision", 0, tokens_used, total_cost)

        return total_cost

    def estimate_multimodal_cost(
        self,
        modality: str,
        duration_seconds: float = 0,
        estimated_tokens: int = 1000,
        image_count: int = 1,
        detail_level: str = "low",
    ) -> float:
        """
        Estimate cost for multimodal processing without tracking.

        Args:
            modality: 'audio' or 'image'
            duration_seconds: Audio duration in seconds
            estimated_tokens: Estimated text tokens for analysis
            image_count: Number of images to process
            detail_level: 'low' or 'high' for images

        Returns:
            Estimated total cost
        """
        if modality == "audio":
            duration_minutes = duration_seconds / 60
            return duration_minutes * self.model_pricing["whisper-1"]["cost_per_minute"]

        elif modality == "image":
            text_cost = self.estimate_cost("gpt-4o", 0, estimated_tokens)
            image_cost_per_unit = self.model_pricing["gpt-4o-vision"][f"image_cost_{detail_level}"]
            image_cost = image_count * image_cost_per_unit
            return text_cost + image_cost

        return 0.0
