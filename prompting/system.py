"""
PromptingSystem - Main orchestrator that integrates all components
"""

import time
from datetime import datetime
from typing import Any, Dict, Optional

# Integration with existing automation framework
from automation.core.context import Context
from automation.core.logger import AutomationLogger

from .core.context_manager import ContextManager
from .core.data_integration import DataIntegrationUnit
from .core.data_laundry import DataLaundry
from .core.inference_engine import InferenceEngine
from .core.insight_synthesizer import InsightSynthesizer
from .core.loop_controller import LoopController
from .core.prompt_router import ModeType, PromptRouter
from .modes.business_mode import BusinessMode
from .modes.concise_mode import ConciseMode
from .modes.conversational_mode import ConversationalMode
from .modes.ide_mode import IDEMode
from .modes.mode_registry import ModeRegistry
from .modes.star_stuff_mode import StarStuffMode


class PromptingSystem:
    """Main prompting system orchestrator"""

    def __init__(
        self,
        storage_path: Optional[str] = None,
        automation_context: Optional[Context] = None,
    ):
        # Core components
        self.router = PromptRouter()
        self.context_manager = ContextManager(storage_path)
        self.inference_engine = InferenceEngine()
        self.data_integration = DataIntegrationUnit()
        self.data_laundry = DataLaundry()
        self.loop_controller = LoopController()
        self.insight_synthesizer = InsightSynthesizer()

        # Mode registry
        self.mode_registry = ModeRegistry()
        self._register_modes()

        # Integration with existing automation framework
        self.automation_context = automation_context
        self.logger = AutomationLogger()

        # System state
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.active_loops = {}

        self.logger.info(f"PromptingSystem initialized - Session: {self.session_id}")

    def _register_modes(self):
        """Register all mode handlers"""
        self.mode_registry.register_mode("concise", ConciseMode())
        self.mode_registry.register_mode("ide", IDEMode())
        self.mode_registry.register_mode("conversational", ConversationalMode())
        self.mode_registry.register_mode("star_stuff", StarStuffMode())
        self.mode_registry.register_mode("business", BusinessMode())

    async def process_prompt(
        self,
        prompt: str,
        mode: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        enable_data_loop: bool = True,
    ) -> Dict[str, Any]:
        """
        Process a prompt through the complete system pipeline

        Args:
            prompt: Input prompt
            mode: Specific mode to use (auto-detect if None)
            context: Additional context
            enable_data_loop: Whether to run data gathering loop

        Returns:
            Complete response with metadata
        """
        start_time = time.perf_counter()

        try:
            # Step 1: Route prompt to appropriate mode
            if mode:
                detected_mode = ModeType(mode)
            else:
                detected_mode = self.router.detect_mode(prompt, context)

            self.logger.info(f"Processing prompt in {detected_mode.value} mode")

            # Step 2: Get context for the mode
            mode_context = self.context_manager.get_context_for_mode(detected_mode.value)
            if context:
                mode_context.update(context)

            # Step 3: Route to processor
            routing_info = self.router.route_to_processor(prompt, detected_mode, mode_context)

            # Step 4: Run inference engine
            inference_result = self.inference_engine.process_prompt(routing_info, mode_context)

            # Step 5: Data integration loop (if enabled)
            if enable_data_loop:
                loop_result = await self._run_data_loop(prompt, inference_result, mode_context)
                inference_result["data_loop_result"] = loop_result

            # Step 6: Format response using mode handler
            mode_handler = self.mode_registry.get_mode(detected_mode.value)
            if mode_handler:
                formatted_response = mode_handler.format_response(inference_result, mode_context)
            else:
                formatted_response = str(inference_result.get("response", {}))

            # Step 7: Add to conversation history
            self.context_manager.add_conversation_entry("user", prompt, detected_mode.value)
            self.context_manager.add_conversation_entry("assistant", formatted_response, detected_mode.value)

            # Step 8: Generate insights
            if enable_data_loop and "data_loop_result" in inference_result:
                insights = self.insight_synthesizer.synthesize_from_loop(
                    inference_result["data_loop_result"], mode_context
                )
                inference_result["insights"] = insights

            duration = time.perf_counter() - start_time
            self.logger.success(f"Prompt processed successfully in {duration:.2f}s")

            return {
                "response": formatted_response,
                "mode": detected_mode.value,
                "metadata": {
                    "session_id": self.session_id,
                    "processing_time": duration,
                    "reasoning_chain": inference_result.get("reasoning_chain", []),
                    "data_sources_used": len(inference_result.get("data_loop_result", {}).get("sources", {})),
                    "insights_generated": len(inference_result.get("insights", {}).get("insights", [])),
                },
                "raw_inference": inference_result,
            }

        except Exception as e:
            self.logger.error(f"Error processing prompt: {e}")
            return {
                "response": f"Error processing prompt: {str(e)}",
                "mode": "error",
                "metadata": {"error": str(e)},
                "raw_inference": {},
            }

    async def _run_data_loop(
        self, prompt: str, inference_result: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run the data integration and refinement loop"""

        # Validation function for loop controller
        async def validate_data(data: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
            quality_score = 0.5  # Base score
            issues = []

            # Check data completeness
            sources = data.get("sources", {})
            if not sources:
                issues.append(
                    {
                        "type": "no_data",
                        "description": "No data sources returned results",
                    }
                )
                quality_score = 0.1
            else:
                successful_sources = sum(1 for s in sources.values() if s.get("status") == "success")
                if len(sources) > 0:
                    quality_score = successful_sources / len(sources)
                else:
                    quality_score = 0.0

            # Check data relevance (simplified)
            total_items = sum(len(s.get("data", [])) for s in sources.values())
            if total_items < 3:
                issues.append(
                    {
                        "type": "insufficient_data",
                        "description": "Too few relevant results",
                    }
                )
                quality_score *= 0.7

            return {
                "quality_score": quality_score,
                "issues": issues,
                "total_items": total_items,
            }

        # Refinement function for loop controller
        async def refine_data(
            data: Dict[str, Any], validation_result: Dict[str, Any], ctx: Dict[str, Any]
        ) -> Dict[str, Any]:
            refinements = []

            # If insufficient data, try different search mode
            if any(issue["type"] == "insufficient_data" for issue in validation_result.get("issues", [])):
                # Switch search strategy
                current_mode = data.get("mode", "technical")
                new_mode = "community" if current_mode == "technical" else "general"

                refined_data = await self.data_integration.gather_data(prompt, ctx, new_mode)
                refinements.append(f"Switched search mode from {current_mode} to {new_mode}")

                # Clean the refined data
                cleaned_data = self.data_laundry.clean_and_filter(refined_data)

                return {"refined_data": cleaned_data, "refinements": refinements}

            return {"refined_data": data, "refinements": refinements}

        # Initial data gathering
        initial_data = await self.data_integration.gather_data(prompt, context)

        # Clean initial data
        cleaned_data = self.data_laundry.clean_and_filter(initial_data)

        # Run feedback loop
        loop_result = await self.loop_controller.run_feedback_loop(
            initial_data=cleaned_data,
            validation_fn=validate_data,
            refinement_fn=refine_data,
            context=context,
        )

        return loop_result

    def set_project_context(self, project_root: str, current_file: str = None):
        """Set project context for the session"""
        self.context_manager.set_project_context(project_root)
        if current_file:
            self.context_manager.set_current_file(current_file)

        self.logger.info(f"Project context set: {project_root}")

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        context_summary = self.context_manager.get_session_summary()
        loop_metrics = self.loop_controller.get_loop_metrics()
        cleaning_stats = self.data_laundry.get_cleaning_stats()

        return {
            "session_id": self.session_id,
            "context": context_summary,
            "loop_metrics": loop_metrics,
            "data_quality": cleaning_stats,
            "available_modes": list(self.mode_registry.list_modes().keys()),
        }

    def create_automation_task(self, task_name: str, prompt: str, mode: str = "ide") -> Dict[str, Any]:
        """
        Create an automation task that can be integrated with the existing framework

        Args:
            task_name: Name for the automation task
            prompt: Prompt to process
            mode: Mode to use for processing

        Returns:
            Task configuration for automation framework
        """
        task_config = {
            "name": task_name,
            "module": "prompting.system",
            "function": "process_prompt_task",
            "params": {"prompt": prompt, "mode": mode, "enable_data_loop": True},
            "description": f"Multi-mode prompting task: {prompt[:50]}...",
        }

        return task_config

    async def process_prompt_task(self, context: Context):
        """
        Task function that can be called by the automation framework

        Args:
            context: Automation framework context
        """
        prompt = context.extra_data.get("prompt", "")
        mode = context.extra_data.get("mode", "conversational")
        enable_data_loop = context.extra_data.get("enable_data_loop", True)

        if not prompt:
            self.logger.error("No prompt provided in automation task")
            return

        # Set automation context
        self.automation_context = context

        # Process the prompt
        result = await self.process_prompt(prompt=prompt, mode=mode, enable_data_loop=enable_data_loop)

        # Log results
        if context.dry_run:
            self.logger.info(f"[DRY-RUN] Would process prompt: {prompt}")
            self.logger.info(f"[DRY-RUN] Mode: {mode}, Response length: {len(result['response'])}")
        else:
            self.logger.success("Processed prompt successfully")
            print(f"\n{'='*60}")
            print(f"PROMPT: {prompt}")
            print(f"MODE: {result['mode'].upper()}")
            print(f"{'='*60}")
            print(result["response"])
            print(f"{'='*60}\n")

    def integrate_with_workflow_macro(self, phases: Dict[str, str]) -> Dict[str, Any]:
        """
        Integrate with the existing workflow macro system

        Args:
            phases: Dictionary mapping phase names to prompts

        Returns:
            Integration configuration
        """
        integration_config = {
            "phases": [],
            "deterministic_merge_config": {"priority_map": {"D": 3, "C": 2, "B": 1, "A": 0}},
        }

        for phase_name, prompt in phases.items():
            phase_config = {
                "name": phase_name,
                "validation_fn": self._create_phase_validator(phase_name),
                "refinement_fn": self._create_phase_refiner(phase_name),
                "prompt": prompt,
            }
            integration_config["phases"].append(phase_config)

        return integration_config

    def _create_phase_validator(self, phase_name: str):
        """Create a validator function for a specific phase"""

        async def validator(data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
            # Phase-specific validation logic
            quality_score = 0.8  # Default good quality
            issues = []

            if phase_name.startswith("phase_a"):  # Baseline phase
                if not data.get("baseline_established"):
                    issues.append(
                        {
                            "type": "missing_baseline",
                            "description": "Baseline not established",
                        }
                    )
                    quality_score = 0.4

            return {"quality_score": quality_score, "issues": issues}

        return validator

    def _create_phase_refiner(self, phase_name: str):
        """Create a refiner function for a specific phase"""

        async def refiner(
            data: Dict[str, Any],
            validation_result: Dict[str, Any],
            context: Dict[str, Any],
        ) -> Dict[str, Any]:
            refinements = []

            # Apply phase-specific refinements
            if phase_name.startswith("phase_a"):
                data["baseline_established"] = True
                refinements.append("Established baseline")

            return {"refined_data": data, "refinements": refinements}

        return refiner


# Global instance for easy access
prompting_system = PromptingSystem()
