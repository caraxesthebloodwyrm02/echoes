"""
Model Router for Echoes Assistant
Routes requests to appropriate language models based on context and requirements
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Available model types"""

    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    CLAUDE = "claude"
    LOCAL = "local"


@dataclass
class ModelConfig:
    """Configuration for a model"""

    name: str
    type: ModelType
    max_tokens: int = 4096
    temperature: float = 0.7
    supports_streaming: bool = True
    cost_per_token: float = 0.0


class ModelRouter:
    """
    Routes requests to appropriate language models based on context and requirements.
    Handles model selection, load balancing, and performance optimization.
    """

    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self.logger = logging.getLogger(__name__)
        self._initialize_default_models()

    def _initialize_default_models(self):
        """Initialize default model configurations"""
        default_models = [
            ModelConfig(
                "gpt-4",
                ModelType.GPT_4,
                max_tokens=8192,
                temperature=0.7,
                cost_per_token=0.03,
            ),
            ModelConfig(
                "gpt-3.5-turbo",
                ModelType.GPT_3_5_TURBO,
                max_tokens=4096,
                temperature=0.7,
                cost_per_token=0.002,
            ),
            ModelConfig(
                "claude-3-opus",
                ModelType.CLAUDE,
                max_tokens=4096,
                temperature=0.7,
                cost_per_token=0.015,
            ),
        ]

        for model in default_models:
            self.models[model.name] = model

    def get_model(self, model_name: str) -> Optional[ModelConfig]:
        """
        Get model configuration by name

        Args:
            model_name: Name of the model

        Returns:
            ModelConfig or None if not found
        """
        return self.models.get(model_name)

    def route_request(self, context: Dict[str, Any]) -> ModelConfig:
        """
        Route a request to the most appropriate model

        Args:
            context: Request context information

        Returns:
            Selected ModelConfig
        """
        # Simple routing logic - can be enhanced
        complexity = context.get("complexity", "medium")
        needs_creativity = context.get("needs_creativity", False)

        if complexity == "high" or needs_creativity:
            return self.models.get("gpt-4", list(self.models.values())[0])
        elif complexity == "low":
            return self.models.get("gpt-3.5-turbo", list(self.models.values())[0])
        else:
            return self.models.get("claude-3-opus", list(self.models.values())[0])

    def get_available_models(self) -> List[str]:
        """
        Get list of available model names

        Returns:
            List of model names
        """
        return list(self.models.keys())

    def add_model(self, config: ModelConfig) -> bool:
        """
        Add a new model configuration

        Args:
            config: Model configuration to add

        Returns:
            True if added successfully
        """
        self.models[config.name] = config
        self.logger.info(f"Added model: {config.name}")
        return True

    def remove_model(self, model_name: str) -> bool:
        """
        Remove a model configuration

        Args:
            model_name: Name of model to remove

        Returns:
            True if removed successfully
        """
        if model_name in self.models:
            del self.models[model_name]
            self.logger.info(f"Removed model: {model_name}")
            return True
        return False


# Global instance for easy access
model_router = ModelRouter()
