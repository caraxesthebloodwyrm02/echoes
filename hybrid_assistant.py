#!/usr/bin/env python3
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
ECHOES Hybrid AI Assistant Implementation
Unified interface for OpenAI, Azure AI, and Local assistant frameworks
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssistantType(Enum):
    """Types of assistants available in the hybrid system"""

    OPENAI = "openai"
    AZURE = "azure"
    LOCAL = "local"
    HYBRID = "hybrid"


class TaskComplexity(Enum):
    """Task complexity levels for routing decisions"""

    SIMPLE = "simple"  # Basic queries, greetings, simple tasks
    MODERATE = "moderate"  # Code analysis, documentation, standard tasks
    COMPLEX = "complex"  # Advanced reasoning, multi-step tasks, creative work


@dataclass
class AssistantCapabilities:
    """Capabilities of each assistant type"""

    supports_code_generation: bool = False
    supports_reasoning: bool = False
    supports_file_operations: bool = False
    supports_api_calls: bool = False
    supports_multimodal: bool = False
    max_context_length: int = 4096
    supports_streaming: bool = False
    cost_per_token: float = 0.0
    response_time: float = 1.0  # seconds


@dataclass
class TaskRequest:
    """Standardized task request format"""

    id: str
    description: str
    complexity: TaskComplexity
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    priority: int = 1


@dataclass
class TaskResponse:
    """Standardized task response format"""

    task_id: str
    assistant_type: AssistantType
    response: str
    confidence: float
    metadata: Dict[str, Any]
    processing_time: float
    cost: float
    timestamp: datetime


@dataclass
class ValidationResult:
    """Cross-validation result between assistants"""

    primary_response: TaskResponse
    secondary_responses: List[TaskResponse]
    consensus_score: float
    discrepancies: List[str]
    recommended_response: TaskResponse


class AssistantRouter:
    """Intelligent routing logic for task distribution"""

    def __init__(self):
        self.routing_strategy = os.getenv("HYBRID_ASSISTANT_DEFAULT_STRATEGY", "auto")
        self.complexity_threshold = float(
            os.getenv("HYBRID_ASSISTANT_COMPLEXITY_THRESHOLD", "0.7")
        )
        self.enable_cross_validation = (
            os.getenv("HYBRID_ASSISTANT_CROSS_VALIDATION", "true").lower() == "true"
        )

        # Define assistant capabilities
        self.capabilities = {
            AssistantType.OPENAI: AssistantCapabilities(
                supports_code_generation=True,
                supports_reasoning=True,
                supports_file_operations=False,
                supports_api_calls=True,
                supports_multimodal=False,
                max_context_length=128000,
                supports_streaming=True,
                cost_per_token=0.00015,
                response_time=2.0,
            ),
            AssistantType.AZURE: AssistantCapabilities(
                supports_code_generation=True,
                supports_reasoning=True,
                supports_file_operations=False,
                supports_api_calls=True,
                supports_multimodal=True,
                max_context_length=128000,
                supports_streaming=True,
                cost_per_token=0.00013,
                response_time=1.8,
            ),
            AssistantType.LOCAL: AssistantCapabilities(
                supports_code_generation=False,
                supports_reasoning=False,
                supports_file_operations=True,
                supports_api_calls=False,
                supports_multimodal=False,
                max_context_length=8192,
                supports_streaming=False,
                cost_per_token=0.0,
                response_time=0.5,
            ),
        }

    def assess_task_complexity(self, task_description: str) -> TaskComplexity:
        """Assess task complexity based on description"""
        description = task_description.lower()

        # Complex indicators
        complex_keywords = [
            "analyze",
            "design",
            "architecture",
            "optimize",
            "debug",
            "implement",
            "create",
            "build",
            "complex",
            "advanced",
            "reasoning",
            "strategy",
            "planning",
            "multiple",
            "integrate",
        ]

        # Simple indicators
        simple_keywords = [
            "hello",
            "hi",
            "what",
            "how are you",
            "status",
            "list",
            "show",
            "display",
            "basic",
            "simple",
        ]

        complex_score = sum(1 for keyword in complex_keywords if keyword in description)
        simple_score = sum(1 for keyword in simple_keywords if keyword in description)

        if complex_score > simple_score:
            return TaskComplexity.COMPLEX
        elif simple_score > complex_score:
            return TaskComplexity.SIMPLE
        else:
            return TaskComplexity.MODERATE

    def select_assistant(self, task: TaskRequest) -> List[AssistantType]:
        """Select appropriate assistant(s) for the task"""

        if self.routing_strategy == "openai":
            return [AssistantType.OPENAI]
        elif self.routing_strategy == "azure":
            return [AssistantType.AZURE]
        elif self.routing_strategy == "local":
            return [AssistantType.LOCAL]
        elif self.routing_strategy == "hybrid":
            return [AssistantType.OPENAI, AssistantType.AZURE]

        # Auto routing logic
        complexity = task.complexity

        if complexity == TaskComplexity.SIMPLE:
            # Simple tasks -> Local assistant (fast, free)
            return [AssistantType.LOCAL]
        elif complexity == TaskComplexity.COMPLEX:
            # Complex tasks -> OpenAI primary, Azure secondary for cross-validation
            assistants = [AssistantType.OPENAI]
            if self.enable_cross_validation:
                assistants.append(AssistantType.AZURE)
            return assistants
        else:  # MODERATE
            # Moderate tasks -> OpenAI primary, with optional cross-validation
            assistants = [AssistantType.OPENAI]
            if task.priority > 1 and self.enable_cross_validation:
                assistants.append(AssistantType.AZURE)
            return assistants


class BaseAssistant:
    """Base class for all assistant implementations"""

    def __init__(self, assistant_type: AssistantType):
        self.type = assistant_type
        self.capabilities = AssistantCapabilities()
        self.is_available = False
        self.last_health_check = None

    async def check_health(self) -> bool:
        """Check if assistant is healthy and available"""
        raise NotImplementedError

    async def process_task(self, task: TaskRequest) -> TaskResponse:
        """Process a task and return response"""
        raise NotImplementedError

    def get_cost_estimate(self, task: TaskRequest) -> float:
        """Estimate cost for processing task"""
        return 0.0


class OpenAIAssistant(BaseAssistant):
    """OpenAI-based assistant implementation"""

    def __init__(self):
        super().__init__(AssistantType.OPENAI)
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("LLM_MODEL_PRIMARY", "gpt-4o-mini")
        self.capabilities = AssistantCapabilities(
            supports_code_generation=True,
            supports_reasoning=True,
            supports_file_operations=False,
            supports_api_calls=True,
            supports_multimodal=False,
            max_context_length=128000,
            supports_streaming=True,
            cost_per_token=0.00015,
            response_time=2.0,
        )

    async def check_health(self) -> bool:
        """Check OpenAI API availability"""
        if not self.api_key:
            self.is_available = False
            return False

        try:
            import openai

            client = openai.AsyncOpenAI(api_key=self.api_key)

            # Simple health check
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
            )

            self.is_available = True
            self.last_health_check = datetime.now()
            return True

        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            self.is_available = False
            return False

    async def process_task(self, task: TaskRequest) -> TaskResponse:
        """Process task with OpenAI"""
        start_time = time.time()

        try:
            import openai

            client = openai.AsyncOpenAI(api_key=self.api_key)

            # Prepare context
            context_str = ""
            if task.context:
                context_str = f"\n\nContext: {json.dumps(task.context, indent=2)}"

            prompt = f"{task.description}{context_str}"

            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=min(4096, self.capabilities.max_context_length // 4),
                temperature=0.7,
            )

            processing_time = time.time() - start_time
            cost = self.get_cost_estimate(task)

            return TaskResponse(
                task_id=task.id,
                assistant_type=self.type,
                response=response.choices[0].message.content,
                confidence=0.85,  # OpenAI typically high confidence
                metadata={
                    "model": self.model,
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                    "finish_reason": response.choices[0].finish_reason,
                },
                processing_time=processing_time,
                cost=cost,
                timestamp=datetime.now(),
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"OpenAI task processing failed: {e}")

            return TaskResponse(
                task_id=task.id,
                assistant_type=self.type,
                response=f"Error: {str(e)}",
                confidence=0.0,
                metadata={"error": str(e)},
                processing_time=processing_time,
                cost=0.0,
                timestamp=datetime.now(),
            )


class AzureAssistant(BaseAssistant):
    """Azure AI-based assistant implementation"""

    def __init__(self):
        super().__init__(AssistantType.AZURE)
        self.endpoint = os.getenv("AZURE_AI_ENDPOINT")
        self.api_key = os.getenv("AZURE_AI_API_KEY")
        self.deployment = os.getenv("AZURE_AI_DEPLOYMENT_NAME", "gpt-4")
        self.api_version = os.getenv("AZURE_AI_API_VERSION", "2024-02-15-preview")

        self.capabilities = AssistantCapabilities(
            supports_code_generation=True,
            supports_reasoning=True,
            supports_file_operations=False,
            supports_api_calls=True,
            supports_multimodal=True,
            max_context_length=128000,
            supports_streaming=True,
            cost_per_token=0.00013,
            response_time=1.8,
        )

    async def check_health(self) -> bool:
        """Check Azure AI availability"""
        if not self.endpoint or not self.api_key:
            self.is_available = False
            return False

        try:
            from azure.ai.inference import ChatCompletionsClient
            from azure.core.credentials import AzureKeyCredential

            client = ChatCompletionsClient(
                endpoint=self.endpoint, credential=AzureKeyCredential(self.api_key)
            )

            # Simple health check
            response = client.complete(
                messages=[{"role": "user", "content": "Hello"}],
                model=self.deployment,
                max_tokens=5,
            )

            self.is_available = True
            self.last_health_check = datetime.now()
            return True

        except Exception as e:
            logger.warning(f"Azure AI health check failed: {e}")
            self.is_available = False
            return False

    async def process_task(self, task: TaskRequest) -> TaskResponse:
        """Process task with Azure AI"""
        start_time = time.time()

        try:
            from azure.ai.inference import ChatCompletionsClient
            from azure.core.credentials import AzureKeyCredential

            client = ChatCompletionsClient(
                endpoint=self.endpoint, credential=AzureKeyCredential(self.api_key)
            )

            # Prepare context
            context_str = ""
            if task.context:
                context_str = f"\n\nContext: {json.dumps(task.context, indent=2)}"

            prompt = f"{task.description}{context_str}"

            response = client.complete(
                messages=[{"role": "user", "content": prompt}],
                model=self.deployment,
                max_tokens=4096,
                temperature=0.7,
            )

            processing_time = time.time() - start_time
            cost = self.get_cost_estimate(task)

            return TaskResponse(
                task_id=task.id,
                assistant_type=self.type,
                response=response.choices[0].message.content,
                confidence=0.82,  # Azure typically slightly lower than OpenAI
                metadata={"model": self.deployment, "endpoint": self.endpoint},
                processing_time=processing_time,
                cost=cost,
                timestamp=datetime.now(),
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Azure AI task processing failed: {e}")

            return TaskResponse(
                task_id=task.id,
                assistant_type=self.type,
                response=f"Error: {str(e)}",
                confidence=0.0,
                metadata={"error": str(e)},
                processing_time=processing_time,
                cost=0.0,
                timestamp=datetime.now(),
            )


class LocalAssistant(BaseAssistant):
    """Local assistant implementation (placeholder for future local AI)"""

    def __init__(self):
        super().__init__(AssistantType.LOCAL)
        self.capabilities = AssistantCapabilities(
            supports_code_generation=False,
            supports_reasoning=False,
            supports_file_operations=True,
            supports_api_calls=False,
            supports_multimodal=False,
            max_context_length=8192,
            supports_streaming=False,
            cost_per_token=0.0,
            response_time=0.5,
        )

    async def check_health(self) -> bool:
        """Local assistant is always available (for now)"""
        self.is_available = True
        self.last_health_check = datetime.now()
        return True

    async def process_task(self, task: TaskRequest) -> TaskResponse:
        """Process simple tasks locally"""
        start_time = time.time()

        # Simple local responses for basic tasks
        description = task.description.lower()

        if "hello" in description or "hi" in description:
            response = (
                "Hello! I'm the local ECHOES assistant. How can I help you today?"
            )
        elif "status" in description:
            response = "Local assistant is operational. All systems nominal."
        elif "list" in description or "show" in description:
            response = "Local file operations available. Please specify what you'd like to list or show."
        else:
            response = f"I understand you want to: {task.description}\n\nFor complex tasks, I recommend using the OpenAI or Azure assistants. Local processing is limited to basic operations."

        processing_time = time.time() - start_time

        return TaskResponse(
            task_id=task.id,
            assistant_type=self.type,
            response=response,
            confidence=0.6,  # Lower confidence for limited local capabilities
            metadata={"local_processing": True},
            processing_time=processing_time,
            cost=0.0,
            timestamp=datetime.now(),
        )


class ResponseValidator:
    """Cross-validation of responses from multiple assistants"""

    def __init__(self):
        pass

    def validate_responses(self, responses: List[TaskResponse]) -> ValidationResult:
        """Validate and compare multiple responses"""

        if len(responses) < 2:
            # Single response - no validation needed
            return ValidationResult(
                primary_response=responses[0],
                secondary_responses=[],
                consensus_score=1.0,
                discrepancies=[],
                recommended_response=responses[0],
            )

        primary = responses[0]
        secondary = responses[1:]

        # Simple consensus scoring based on response similarity
        consensus_score = self._calculate_consensus(primary, secondary)
        discrepancies = self._identify_discrepancies(primary, secondary)

        # Select recommended response (highest confidence, then fastest)
        recommended = max(responses, key=lambda r: (r.confidence, -r.processing_time))

        return ValidationResult(
            primary_response=primary,
            secondary_responses=secondary,
            consensus_score=consensus_score,
            discrepancies=discrepancies,
            recommended_response=recommended,
        )

    def _calculate_consensus(
        self, primary: TaskResponse, secondary: List[TaskResponse]
    ) -> float:
        """Calculate consensus score between responses"""
        # Simple implementation - in production, use semantic similarity
        similarities = []

        primary_words = set(primary.response.lower().split())
        for resp in secondary:
            secondary_words = set(resp.response.lower().split())
            intersection = primary_words.intersection(secondary_words)
            union = primary_words.union(secondary_words)
            similarity = len(intersection) / len(union) if union else 0.0
            similarities.append(similarity)

        return sum(similarities) / len(similarities) if similarities else 1.0

    def _identify_discrepancies(
        self, primary: TaskResponse, secondary: List[TaskResponse]
    ) -> List[str]:
        """Identify discrepancies between responses"""
        discrepancies = []

        # Check for major differences in response length
        primary_length = len(primary.response.split())
        for resp in secondary:
            secondary_length = len(resp.response.split())
            if abs(primary_length - secondary_length) > primary_length * 0.5:
                discrepancies.append(
                    f"Response length discrepancy: {primary_length} vs {secondary_length} words"
                )

        # Check for error responses
        for resp in secondary:
            if "error" in resp.response.lower() or "failed" in resp.response.lower():
                discrepancies.append(
                    f"{resp.assistant_type.value} assistant reported an error"
                )

        return discrepancies


class UnifiedAssistant:
    """Unified interface for hybrid AI assistant system"""

    def __init__(self):
        self.router = AssistantRouter()
        self.validator = ResponseValidator()

        # Initialize assistants
        self.assistants = {
            AssistantType.OPENAI: OpenAIAssistant(),
            AssistantType.AZURE: AzureAssistant(),
            AssistantType.LOCAL: LocalAssistant(),
        }

        # Performance monitoring
        self.enable_monitoring = (
            os.getenv("HYBRID_ASSISTANT_MONITORING", "true").lower() == "true"
        )
        self.performance_log = []

        logger.info("UnifiedAssistant initialized with hybrid capabilities")

    async def initialize(self):
        """Initialize all assistants and check health"""
        logger.info("Initializing hybrid assistant system...")

        health_results = {}
        for assistant_type, assistant in self.assistants.items():
            try:
                is_healthy = await assistant.check_health()
                health_results[assistant_type.value] = is_healthy
                logger.info(
                    f"{assistant_type.value} assistant health: {'OK' if is_healthy else 'FAILED'}"
                )
            except Exception as e:
                health_results[assistant_type.value] = False
                logger.error(
                    f"{assistant_type.value} assistant initialization failed: {e}"
                )

        healthy_count = sum(1 for status in health_results.values() if status)
        logger.info(
            f"Assistant initialization complete: {healthy_count}/{len(self.assistants)} healthy"
        )

        return health_results

    async def process_task(
        self, task_description: str, context: Dict[str, Any] = None, priority: int = 1
    ) -> TaskResponse:
        """Process a task using the hybrid assistant system"""

        # Create standardized task request
        task = TaskRequest(
            id=f"task_{int(time.time() * 1000)}",
            description=task_description,
            complexity=self.router.assess_task_complexity(task_description),
            context=context or {},
            metadata={},
            timestamp=datetime.now(),
            priority=priority,
        )

        logger.info(f"Processing task {task.id}: {task.complexity.value} complexity")

        # Select appropriate assistants
        selected_assistants = self.router.select_assistant(task)
        logger.info(f"Selected assistants: {[a.value for a in selected_assistants]}")

        # Process with selected assistants
        responses = []
        for assistant_type in selected_assistants:
            assistant = self.assistants[assistant_type]
            if assistant.is_available:
                try:
                    response = await assistant.process_task(task)
                    responses.append(response)
                    logger.info(
                        f"{assistant_type.value} processing complete in {response.processing_time:.2f}s"
                    )
                except Exception as e:
                    logger.error(f"{assistant_type.value} processing failed: {e}")
            else:
                logger.warning(
                    f"{assistant_type.value} assistant not available, skipping"
                )

        if not responses:
            # Fallback to local assistant
            logger.warning("No assistants available, using local fallback")
            local_assistant = self.assistants[AssistantType.LOCAL]
            response = await local_assistant.process_task(task)
            responses.append(response)

        # Validate responses if multiple
        if len(responses) > 1:
            validation = self.validator.validate_responses(responses)
            logger.info(f"Cross-validation consensus: {validation.consensus_score:.2f}")

            if self.enable_monitoring:
                self._log_performance(task, responses, validation)

            return validation.recommended_response
        else:
            if self.enable_monitoring:
                self._log_performance(task, responses, None)

            return responses[0]

    async def get_status(self) -> Dict[str, Any]:
        """Get system status and health information"""

        status = {
            "timestamp": datetime.now().isoformat(),
            "assistants": {},
            "system_health": "unknown",
            "total_tasks_processed": len(self.performance_log),
        }

        healthy_assistants = 0
        for assistant_type, assistant in self.assistants.items():
            assistant_status = {
                "available": assistant.is_available,
                "last_health_check": (
                    assistant.last_health_check.isoformat()
                    if assistant.last_health_check
                    else None
                ),
                "capabilities": asdict(assistant.capabilities),
            }
            status["assistants"][assistant_type.value] = assistant_status

            if assistant.is_available:
                healthy_assistants += 1

        # Determine overall system health
        if healthy_assistants == len(self.assistants):
            status["system_health"] = "excellent"
        elif healthy_assistants >= 2:
            status["system_health"] = "good"
        elif healthy_assistants >= 1:
            status["system_health"] = "degraded"
        else:
            status["system_health"] = "critical"

        return status

    def _log_performance(
        self,
        task: TaskRequest,
        responses: List[TaskResponse],
        validation: ValidationResult = None,
    ):
        """Log performance metrics"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task.id,
            "task_complexity": task.complexity.value,
            "assistants_used": [r.assistant_type.value for r in responses],
            "responses": [
                {
                    "assistant": r.assistant_type.value,
                    "processing_time": r.processing_time,
                    "cost": r.cost,
                    "confidence": r.confidence,
                }
                for r in responses
            ],
        }

        if validation:
            log_entry["validation"] = {
                "consensus_score": validation.consensus_score,
                "discrepancies_count": len(validation.discrepancies),
                "recommended_assistant": validation.recommended_response.assistant_type.value,
            }

        self.performance_log.append(log_entry)

        # Keep only last 1000 entries
        if len(self.performance_log) > 1000:
            self.performance_log = self.performance_log[-1000:]

    def export_performance_log(self, filepath: str = None) -> str:
        """Export performance log to file"""

        if not filepath:
            os.makedirs("reports", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"reports/hybrid_assistant_performance_{timestamp}.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.performance_log, f, indent=2, ensure_ascii=False)

        return filepath


# Global instance
_unified_assistant = None


async def create_unified_assistant() -> UnifiedAssistant:
    """Factory function to create and initialize unified assistant"""

    global _unified_assistant

    if _unified_assistant is None:
        _unified_assistant = UnifiedAssistant()
        await _unified_assistant.initialize()

    return _unified_assistant


# Synchronous wrapper for backward compatibility
def create_unified_assistant_sync() -> UnifiedAssistant:
    """Synchronous factory function (initializes but doesn't check health)"""

    global _unified_assistant

    if _unified_assistant is None:
        _unified_assistant = UnifiedAssistant()
        # Note: Health checks require async, so this creates but doesn't initialize

    return _unified_assistant


if __name__ == "__main__":
    # Example usage
    async def main():
        print("ECHOES Hybrid Assistant Demo")
        print("=" * 40)

        # Create and initialize assistant
        assistant = await create_unified_assistant()

        # Get status
        status = await assistant.get_status()
        print(f"System Health: {status['system_health']}")
        print(
            f"Available Assistants: {sum(1 for a in status['assistants'].values() if a['available'])}"
        )

        # Process sample tasks
        tasks = [
            "Hello, how are you?",
            "Analyze this Python code for potential bugs",
            "Create a plan for implementing user authentication",
        ]

        for task in tasks:
            print(f"\nTask: {task}")
            response = await assistant.process_task(task)
            print(f"Assistant: {response.assistant_type.value}")
            print(f"Response: {response.response[:100]}...")
            print(f"Processing time: {response.processing_time:.2f}s")

        # Export performance log
        log_file = assistant.export_performance_log()
        print(f"\nPerformance log saved to: {log_file}")

    # Run demo
    asyncio.run(main())
