"""
Parallel Simulation Engine - Runs multiple concurrent instances to explore possibilities
Enhances cross-references by simulating different scenarios and outcomes in parallel
"""

import logging
import queue
import threading
import time
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class SimulationType(Enum):
    """Types of parallel simulations"""

    SCENARIO_EXPLORATION = "scenario_exploration"  # Explore different scenarios
    OUTCOME_PREDICTION = "outcome_prediction"  # Predict possible outcomes
    ALTERNATIVE_PATHS = "alternative_paths"  # Simulate alternative approaches
    CONTEXT_EXPANSION = "context_expansion"  # Expand context with related info
    CROSS_REFERENCE_ENHANCEMENT = "cross_ref_enhancement"  # Enhance cross-references
    POSSIBILITY_SPACE = "possibility_space"  # Map out possibility space
    DECISION_SUPPORT = "decision_support"  # Support decision making


class SimulationStatus(Enum):
    """Status of simulation instances"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SimulationInstance:
    """A single simulation instance"""

    id: str
    simulation_type: SimulationType
    input_data: dict[str, Any]
    parameters: dict[str, Any]
    status: SimulationStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
    confidence: float = 0.0
    relevance_score: float = 0.0
    parent_id: str | None = None
    child_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationResult:
    """Result of a simulation with analysis"""

    instance_id: str
    simulation_type: SimulationType
    outcome: dict[str, Any]
    confidence: float
    reasoning: str
    insights: list[str]
    cross_references: list[dict[str, Any]]
    possibilities: list[dict[str, Any]]
    execution_time: float


class ParallelSimulationEngine:
    """Manages parallel simulation instances for possibility exploration"""

    def __init__(self, max_workers: int = 8, max_concurrent_simulations: int = 16):
        self.max_workers = max_workers
        self.max_concurrent_simulations = max_concurrent_simulations

        # Speed control
        self.speed_multiplier = 1.0  # Higher values = faster processing

        # Simulation storage
        self.simulations: dict[str, SimulationInstance] = {}
        self.simulation_queue = queue.Queue()
        self.active_simulations: dict[str, threading.Thread] = {}

        # Thread pool for execution
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Cross-reference integration
        self.cross_reference_callbacks: list[Callable] = []

        # Statistics
        self.stats = {
            "total_simulations": 0,
            "completed_simulations": 0,
            "failed_simulations": 0,
            "average_execution_time": 0.0,
            "total_execution_time": 0.0,
        }

        # Simulation templates
        self.simulation_templates = self._initialize_templates()

        # Background processor
        self.running = True
        self.processor_thread = threading.Thread(
            target=self._process_simulation_queue, daemon=True
        )
        self.processor_thread.start()

    def _initialize_templates(self) -> dict[SimulationType, Callable]:
        """Initialize simulation templates"""
        return {
            SimulationType.SCENARIO_EXPLORATION: self._simulate_scenario_exploration,
            SimulationType.OUTCOME_PREDICTION: self._simulate_outcome_prediction,
            SimulationType.ALTERNATIVE_PATHS: self._simulate_alternative_paths,
            SimulationType.CONTEXT_EXPANSION: self._simulate_context_expansion,
            SimulationType.CROSS_REFERENCE_ENHANCEMENT: self._simulate_cross_reference_enhancement,
            SimulationType.POSSIBILITY_SPACE: self._simulate_possibility_space,
            SimulationType.DECISION_SUPPORT: self._simulate_decision_support,
        }

    def set_speed_multiplier(self, multiplier: float):
        """Set speed multiplier for simulation processing (higher = faster)"""
        self.speed_multiplier = max(
            0.1, multiplier
        )  # Prevent division by zero or too slow

    def create_simulation(
        self,
        simulation_type: SimulationType,
        input_data: dict[str, Any],
        parameters: dict[str, Any] = None,
        parent_id: str = None,
    ) -> str:
        """Create a new simulation instance"""

        simulation_id = str(uuid.uuid4())

        instance = SimulationInstance(
            id=simulation_id,
            simulation_type=simulation_type,
            input_data=input_data,
            parameters=parameters or {},
            status=SimulationStatus.PENDING,
            created_at=datetime.now(),
            parent_id=parent_id,
            metadata={
                "priority": parameters.get("priority", 0.5) if parameters else 0.5,
                "timeout": parameters.get("timeout", 30) if parameters else 30,
            },
        )

        self.simulations[simulation_id] = instance

        # Add to queue for processing
        self.simulation_queue.put(simulation_id)

        self.stats["total_simulations"] += 1

        logger.debug(f"Created simulation {simulation_id}: {simulation_type.value}")
        return simulation_id

    def _process_simulation_queue(self):
        """Background thread to process simulation queue"""
        while self.running:
            try:
                # Get simulation from queue
                simulation_id = self.simulation_queue.get(timeout=1)

                if simulation_id not in self.simulations:
                    continue

                self.simulations[simulation_id]

                # Check if we can run this simulation
                if len(self.active_simulations) >= self.max_concurrent_simulations:
                    # Re-queue if at capacity
                    self.simulation_queue.put(simulation_id)
                    time.sleep(0.1 / self.speed_multiplier)
                    continue

                # Start simulation in thread pool
                future = self.executor.submit(self._run_simulation, simulation_id)

                # Track active simulation
                self.active_simulations[simulation_id] = future

                logger.debug(f"Started simulation {simulation_id}")

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing simulation queue: {e}")

    def _run_simulation(self, simulation_id: str) -> SimulationResult:
        """Execute a simulation instance"""

        instance = self.simulations[simulation_id]

        try:
            # Update status
            instance.status = SimulationStatus.RUNNING
            instance.started_at = datetime.now()

            # Get simulation function
            sim_function = self.simulation_templates.get(instance.simulation_type)
            if not sim_function:
                raise ValueError(
                    f"No simulation function for {instance.simulation_type}"
                )

            # Execute simulation
            start_time = time.time()
            result = sim_function(instance.input_data, instance.parameters)
            execution_time = time.time() - start_time

            # Create simulation result
            sim_result = SimulationResult(
                instance_id=simulation_id,
                simulation_type=instance.simulation_type,
                outcome=result.get("outcome", {}),
                confidence=result.get("confidence", 0.5),
                reasoning=result.get("reasoning", ""),
                insights=result.get("insights", []),
                cross_references=result.get("cross_references", []),
                possibilities=result.get("possibilities", []),
                execution_time=execution_time,
            )

            # Update instance
            instance.status = SimulationStatus.COMPLETED
            instance.completed_at = datetime.now()
            instance.result = asdict(sim_result)
            instance.confidence = sim_result.confidence
            instance.relevance_score = result.get("relevance_score", 0.5)

            # Update statistics
            self.stats["completed_simulations"] += 1
            self.stats["total_execution_time"] += execution_time
            self.stats["average_execution_time"] = (
                self.stats["total_execution_time"] / self.stats["completed_simulations"]
            )

            # Trigger cross-reference callbacks
            self._trigger_cross_reference_callbacks(sim_result)

            logger.debug(
                f"Completed simulation {simulation_id} in {execution_time:.2f}s"
            )

            return sim_result

        except Exception as e:
            # Handle simulation failure
            instance.status = SimulationStatus.FAILED
            instance.completed_at = datetime.now()
            instance.error = str(e)

            self.stats["failed_simulations"] += 1

            logger.error(f"Simulation {simulation_id} failed: {e}")

            # Return error result
            return SimulationResult(
                instance_id=simulation_id,
                simulation_type=instance.simulation_type,
                outcome={"error": str(e)},
                confidence=0.0,
                reasoning=f"Simulation failed: {str(e)}",
                insights=[],
                cross_references=[],
                possibilities=[],
                execution_time=0.0,
            )

        finally:
            # Remove from active simulations
            if simulation_id in self.active_simulations:
                del self.active_simulations[simulation_id]

    def _simulate_scenario_exploration(
        self, input_data: dict[str, Any], parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Simulate different scenarios based on input"""

        base_scenario = input_data.get("scenario", "")
        input_data.get("context", {})

        # Generate alternative scenarios
        scenarios = []

        # Scenario variations
        variations = [
            f"What if {base_scenario} fails?",
            f"Best case scenario for {base_scenario}",
            f"Worst case scenario for {base_scenario}",
            f"Alternative approach to {base_scenario}",
            f"Optimized version of {base_scenario}",
        ]

        for variation in variations:
            scenarios.append(
                {
                    "description": variation,
                    "likelihood": 0.6 + (len(scenarios) * 0.1),
                    "impact": "medium" if len(scenarios) % 2 == 0 else "high",
                    "requirements": self._extract_requirements(variation),
                }
            )

        return {
            "outcome": {
                "scenarios": scenarios,
                "total_explored": len(scenarios),
                "recommendation": scenarios[0] if scenarios else None,
            },
            "confidence": 0.7,
            "reasoning": f"Explored {len(scenarios)} scenarios based on {base_scenario}",
            "insights": [
                "Multiple scenarios provide risk mitigation",
                "Alternative paths increase success probability",
                "Context factors influence scenario outcomes",
            ],
            "cross_references": [
                {"type": "scenario", "target": "risk_assessment", "strength": 0.8},
                {"type": "scenario", "target": "decision_tree", "strength": 0.7},
            ],
            "possibilities": scenarios,
            "relevance_score": 0.8,
        }

    def _simulate_outcome_prediction(
        self, input_data: dict[str, Any], parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Predict possible outcomes for a given situation"""

        action = input_data.get("action", "")
        input_data.get("context", {})

        # Predict outcomes
        outcomes = []

        # Success outcome
        outcomes.append(
            {
                "type": "success",
                "probability": 0.65,
                "description": f"{action} succeeds with expected results",
                "timeline": "2-4 weeks",
                "dependencies": ["resources", "timing", "expertise"],
            }
        )

        # Partial success outcome
        outcomes.append(
            {
                "type": "partial_success",
                "probability": 0.25,
                "description": f"{action} partially succeeds, needs refinement",
                "timeline": "4-6 weeks",
                "dependencies": ["iteration", "feedback", "adjustment"],
            }
        )

        # Failure outcome
        outcomes.append(
            {
                "type": "failure",
                "probability": 0.10,
                "description": f"{action} fails, requires restart",
                "timeline": "6-8 weeks",
                "dependencies": ["recovery", "replanning", "additional_resources"],
            }
        )

        return {
            "outcome": {
                "predicted_outcomes": outcomes,
                "most_likely": max(outcomes, key=lambda x: x["probability"]),
                "risk_assessment": "medium"
                if outcomes[0]["probability"] > 0.5
                else "high",
            },
            "confidence": 0.75,
            "reasoning": f"Predicted outcomes for {action} based on context analysis",
            "insights": [
                "Success probability is favorable",
                "Contingency planning recommended",
                "Timeline estimates depend on execution quality",
            ],
            "cross_references": [
                {"type": "prediction", "target": "risk_management", "strength": 0.9},
                {"type": "prediction", "target": "timeline_planning", "strength": 0.8},
            ],
            "possibilities": outcomes,
            "relevance_score": 0.85,
        }

    def _simulate_alternative_paths(
        self, input_data: dict[str, Any], parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Simulate alternative approaches to a problem"""

        problem = input_data.get("problem", "")
        input_data.get("current_approach", "")

        alternatives = []

        # Alternative 1: Technology-focused
        alternatives.append(
            {
                "name": "Technology-Driven Approach",
                "description": f"Use advanced technology to solve {problem}",
                "pros": ["scalable", "efficient", "innovative"],
                "cons": ["complex", "requires expertise", "initial cost"],
                "effort": "high",
                "timeline": "8-12 weeks",
                "success_probability": 0.7,
            }
        )

        # Alternative 2: Process-focused
        alternatives.append(
            {
                "name": "Process-Optimization Approach",
                "description": f"Optimize existing processes to address {problem}",
                "pros": ["quick wins", "low cost", "minimal disruption"],
                "cons": ["limited scope", "incremental", "maintenance required"],
                "effort": "medium",
                "timeline": "4-6 weeks",
                "success_probability": 0.8,
            }
        )

        # Alternative 3: Hybrid approach
        alternatives.append(
            {
                "name": "Hybrid Approach",
                "description": f"Combine technology and process improvements for {problem}",
                "pros": ["balanced", "flexible", "risk distributed"],
                "cons": ["coordination complexity", "integration challenges"],
                "effort": "medium-high",
                "timeline": "6-10 weeks",
                "success_probability": 0.75,
            }
        )

        return {
            "outcome": {
                "alternatives": alternatives,
                "recommended": max(
                    alternatives, key=lambda x: x["success_probability"]
                ),
                "comparison": self._compare_alternatives(alternatives),
            },
            "confidence": 0.8,
            "reasoning": f"Generated {len(alternatives)} alternative approaches for {problem}",
            "insights": [
                "Multiple alternatives provide flexibility",
                "Each approach has distinct trade-offs",
                "Hybrid solutions often balance risk and reward",
            ],
            "cross_references": [
                {"type": "alternative", "target": "decision_analysis", "strength": 0.9},
                {"type": "alternative", "target": "solution_design", "strength": 0.8},
            ],
            "possibilities": alternatives,
            "relevance_score": 0.9,
        }

    def _simulate_context_expansion(
        self, input_data: dict[str, Any], parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Expand context with related information"""

        topic = input_data.get("topic", "")
        input_data.get("context", {})

        # Expand context with related domains
        expansions = []

        # Domain expansion
        related_domains = self._find_related_domains(topic)
        for domain in related_domains:
            expansions.append(
                {
                    "type": "domain",
                    "content": domain,
                    "relevance": 0.8,
                    "description": f"Related domain: {domain}",
                }
            )

        # Historical context
        historical_context = self._generate_historical_context(topic)
        expansions.append(
            {
                "type": "historical",
                "content": historical_context,
                "relevance": 0.7,
                "description": "Historical background and evolution",
            }
        )

        # Future implications
        future_implications = self._generate_future_implications(topic)
        expansions.append(
            {
                "type": "future",
                "content": future_implications,
                "relevance": 0.8,
                "description": "Future trends and implications",
            }
        )

        return {
            "outcome": {
                "expanded_context": expansions,
                "context_areas": list({exp["type"] for exp in expansions}),
                "breadth": len(expansions),
                "depth": "medium",
            },
            "confidence": 0.75,
            "reasoning": f"Expanded context for {topic} with {len(expansions)} dimensions",
            "insights": [
                "Multi-dimensional context provides richer understanding",
                "Historical perspective informs current decisions",
                "Future implications guide strategic planning",
            ],
            "cross_references": [
                {"type": "context", "target": "domain_knowledge", "strength": 0.8},
                {"type": "context", "target": "trend_analysis", "strength": 0.7},
            ],
            "possibilities": expansions,
            "relevance_score": 0.8,
        }

    def _simulate_cross_reference_enhancement(
        self, input_data: dict[str, Any], parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Enhance cross-references with simulation insights"""

        query = input_data.get("query", "")
        existing_refs = input_data.get("existing_references", [])

        # Generate enhanced cross-references
        enhanced_refs = []

        # Simulate finding deeper connections
        deep_connections = [
            {
                "type": "causal",
                "description": f"Causal relationships related to {query}",
                "strength": 0.9,
                "explanation": "Understanding cause and effect chains",
            },
            {
                "type": "analogical",
                "description": f"Analogous situations to {query}",
                "strength": 0.8,
                "explanation": "Learning from similar patterns in other domains",
            },
            {
                "type": "temporal",
                "description": f"Temporal evolution of {query}",
                "strength": 0.7,
                "explanation": "How this topic has evolved over time",
            },
        ]

        # Combine with existing references
        all_refs = existing_refs + deep_connections

        for ref in all_refs:
            enhanced_refs.append(
                {
                    **ref,
                    "enhanced": True,
                    "simulation_insights": self._generate_insights_for_reference(ref),
                    "confidence_boost": 0.1,
                }
            )

        return {
            "outcome": {
                "enhanced_references": enhanced_refs,
                "original_count": len(existing_refs),
                "enhanced_count": len(enhanced_refs),
                "improvement": len(enhanced_refs) - len(existing_refs),
            },
            "confidence": 0.85,
            "reasoning": f"Enhanced {len(existing_refs)} existing references with simulation insights",
            "insights": [
                "Cross-references benefit from multi-dimensional analysis",
                "Simulation reveals hidden connections",
                "Enhanced references provide richer context",
            ],
            "cross_references": enhanced_refs,
            "possibilities": deep_connections,
            "relevance_score": 0.9,
        }

    def _simulate_possibility_space(
        self, input_data: dict[str, Any], parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Map out the entire possibility space for a topic"""

        topic = input_data.get("topic", "")
        input_data.get("constraints", {})

        # Generate possibility space dimensions
        dimensions = []

        # Technical possibilities
        tech_possibilities = [
            "Current technology approach",
            "Next-generation technology",
            "Emerging technology integration",
            "Legacy system modernization",
            "Custom solution development",
        ]

        dimensions.append(
            {
                "name": "technical",
                "possibilities": tech_possibilities,
                "complexity": "high",
                "impact": "transformative",
            }
        )

        # Business possibilities
        business_possibilities = [
            "Incremental improvement",
            "Process optimization",
            "Business model innovation",
            "Market expansion",
            "Disruptive innovation",
        ]

        dimensions.append(
            {
                "name": "business",
                "possibilities": business_possibilities,
                "complexity": "medium",
                "impact": "strategic",
            }
        )

        # Resource possibilities
        resource_possibilities = [
            "Internal resource allocation",
            "External partnership",
            "Open-source collaboration",
            "Acquisition strategy",
            "Shared resource model",
        ]

        dimensions.append(
            {
                "name": "resource",
                "possibilities": resource_possibilities,
                "complexity": "medium",
                "impact": "operational",
            }
        )

        # Calculate total combinations
        total_combinations = 1
        for dim in dimensions:
            total_combinations *= len(dim["possibilities"])

        return {
            "outcome": {
                "possibility_space": dimensions,
                "total_dimensions": len(dimensions),
                "total_combinations": total_combinations,
                "exploration_recommendation": "Start with low-complexity, high-impact options",
            },
            "confidence": 0.7,
            "reasoning": f"Mapped possibility space for {topic} with {total_combinations} combinations",
            "insights": [
                f"Vast possibility space with {total_combinations} combinations",
                "Multi-dimensional approach reveals hidden options",
                "Strategic prioritization is essential for exploration",
            ],
            "cross_references": [
                {
                    "type": "possibility",
                    "target": "strategic_planning",
                    "strength": 0.9,
                },
                {
                    "type": "possibility",
                    "target": "innovation_management",
                    "strength": 0.8,
                },
            ],
            "possibilities": [p for dim in dimensions for p in dim["possibilities"]],
            "relevance_score": 0.85,
        }

    def _simulate_decision_support(
        self, input_data: dict[str, Any], parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Provide decision support through simulation"""

        decision = input_data.get("decision", "")
        options = input_data.get("options", [])
        input_data.get("criteria", {})

        # Simulate decision outcomes for each option
        option_analyses = []

        for i, option in enumerate(options):
            analysis = {
                "option": option,
                "success_probability": 0.5 + (i * 0.1),  # Varying probabilities
                "expected_outcome": f"Positive outcome if {option} chosen",
                "risks": [f"Risk {j + 1} for {option}" for j in range(2)],
                "benefits": [f"Benefit {j + 1} for {option}" for j in range(3)],
                "timeline": f"{4 + i} weeks",
                "resource_requirements": ["team", "budget", "technology"],
                "confidence": 0.7 + (i * 0.05),
            }
            option_analyses.append(analysis)

        # Generate recommendation
        best_option = max(option_analyses, key=lambda x: x["success_probability"])

        return {
            "outcome": {
                "option_analyses": option_analyses,
                "recommended_option": best_option,
                "decision_framework": "Multi-criteria analysis with simulation",
                "confidence_in_recommendation": best_option["confidence"],
            },
            "confidence": 0.8,
            "reasoning": f"Analyzed {len(options)} options for decision: {decision}",
            "insights": [
                "Simulation reveals probability-based decision factors",
                "Multi-criteria analysis balances competing priorities",
                "Risk-benefit assessment informs strategic choices",
            ],
            "cross_references": [
                {"type": "decision", "target": "risk_assessment", "strength": 0.9},
                {"type": "decision", "target": "outcome_prediction", "strength": 0.8},
            ],
            "possibilities": option_analyses,
            "relevance_score": 0.9,
        }

    def get_simulation_result(self, simulation_id: str) -> SimulationResult | None:
        """Get result of a specific simulation"""

        if simulation_id not in self.simulations:
            return None

        instance = self.simulations[simulation_id]

        if instance.status == SimulationStatus.COMPLETED and instance.result:
            return SimulationResult(**instance.result)

        return None

    def get_simulation_status(self, simulation_id: str) -> SimulationInstance | None:
        """Get status of a simulation"""
        return self.simulations.get(simulation_id)

    def wait_for_simulation(
        self, simulation_id: str, timeout: float = 30.0
    ) -> SimulationResult | None:
        """Wait for simulation to complete"""

        start_time = time.time()

        while time.time() - start_time < timeout:
            instance = self.simulations.get(simulation_id)
            if not instance:
                return None

            if instance.status == SimulationStatus.COMPLETED:
                return self.get_simulation_result(simulation_id)
            elif instance.status == SimulationStatus.FAILED:
                return self.get_simulation_result(simulation_id)

            time.sleep(0.1 / self.speed_multiplier)

        return None

    def run_parallel_simulations(
        self, simulation_configs: list[dict[str, Any]]
    ) -> list[SimulationResult]:
        """Run multiple simulations in parallel"""

        simulation_ids = []

        # Create all simulations
        for config in simulation_configs:
            sim_id = self.create_simulation(
                simulation_type=config["type"],
                input_data=config["input_data"],
                parameters=config.get("parameters", {}),
            )
            simulation_ids.append(sim_id)

        # Wait for all to complete
        results = []
        for sim_id in simulation_ids:
            result = self.wait_for_simulation(sim_id, timeout=60.0)
            if result:
                results.append(result)

        return results

    def add_cross_reference_callback(
        self, callback: Callable[[SimulationResult], None]
    ):
        """Add callback for cross-reference enhancement"""
        self.cross_reference_callbacks.append(callback)

    def _trigger_cross_reference_callbacks(self, result: SimulationResult):
        """Trigger all cross-reference callbacks"""
        for callback in self.cross_reference_callbacks:
            try:
                callback(result)
            except Exception as e:
                logger.error(f"Error in cross-reference callback: {e}")

    def _extract_requirements(self, scenario: str) -> list[str]:
        """Extract requirements from scenario description"""
        # Simple requirement extraction
        requirements = []
        if "resource" in scenario.lower():
            requirements.append("resources")
        if "time" in scenario.lower():
            requirements.append("time")
        if "expertise" in scenario.lower():
            requirements.append("expertise")
        if "technology" in scenario.lower():
            requirements.append("technology")
        return requirements

    def _compare_alternatives(
        self, alternatives: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Compare alternative approaches"""
        if not alternatives:
            return {}

        # Sort by success probability
        sorted_alts = sorted(
            alternatives, key=lambda x: x["success_probability"], reverse=True
        )

        return {
            "best": sorted_alts[0],
            "worst": sorted_alts[-1],
            "average_success": sum(alt["success_probability"] for alt in alternatives)
            / len(alternatives),
            "effort_range": {
                "min": min(alt.get("effort", "medium") for alt in alternatives),
                "max": max(alt.get("effort", "medium") for alt in alternatives),
            },
        }

    def _find_related_domains(self, topic: str) -> list[str]:
        """Find domains related to topic"""
        # Simple domain mapping
        domain_map = {
            "ai": ["machine learning", "data science", "neural networks", "automation"],
            "software": ["development", "programming", "architecture", "testing"],
            "business": ["strategy", "management", "marketing", "finance"],
            "technology": ["innovation", "research", "engineering", "digital"],
        }

        topic_lower = topic.lower()
        for key, domains in domain_map.items():
            if key in topic_lower:
                return domains[:3]  # Return top 3

        return ["general", "interdisciplinary", "applied"]

    def _generate_historical_context(self, topic: str) -> str:
        """Generate historical context for topic"""
        return f"Historical evolution of {topic} shows progressive development from early concepts to modern applications"

    def _generate_future_implications(self, topic: str) -> str:
        """Generate future implications for topic"""
        return f"Future trends in {topic} indicate increased integration with emerging technologies and expanding applications"

    def _generate_insights_for_reference(self, reference: dict[str, Any]) -> list[str]:
        """Generate insights for a specific reference"""
        insights = []
        ref_type = reference.get("type", "")

        if ref_type == "causal":
            insights.append("Understanding causal chains enables prediction")
        elif ref_type == "analogical":
            insights.append("Analogous patterns provide transferable insights")
        elif ref_type == "temporal":
            insights.append("Historical context informs future trajectories")

        return insights

    def get_simulation_statistics(self) -> dict[str, Any]:
        """Get comprehensive simulation statistics"""

        # Status breakdown
        status_counts = {}
        for status in SimulationStatus:
            status_counts[status.value] = sum(
                1 for sim in self.simulations.values() if sim.status == status
            )

        # Type breakdown
        type_counts = {}
        for sim_type in SimulationType:
            type_counts[sim_type.value] = sum(
                1
                for sim in self.simulations.values()
                if sim.simulation_type == sim_type
            )

        # Performance metrics
        completed_sims = [
            sim
            for sim in self.simulations.values()
            if sim.status == SimulationStatus.COMPLETED
        ]

        if completed_sims:
            avg_confidence = sum(sim.confidence for sim in completed_sims) / len(
                completed_sims
            )
            avg_relevance = sum(sim.relevance_score for sim in completed_sims) / len(
                completed_sims
            )
        else:
            avg_confidence = 0.0
            avg_relevance = 0.0

        return {
            "total_simulations": len(self.simulations),
            "active_simulations": len(self.active_simulations),
            "status_breakdown": status_counts,
            "type_breakdown": type_counts,
            "performance": {
                "completed": self.stats["completed_simulations"],
                "failed": self.stats["failed_simulations"],
                "success_rate": (
                    self.stats["completed_simulations"]
                    / max(self.stats["total_simulations"], 1)
                ),
                "average_execution_time": self.stats["average_execution_time"],
                "average_confidence": avg_confidence,
                "average_relevance": avg_relevance,
            },
            "queue_size": self.simulation_queue.qsize(),
            "max_workers": self.max_workers,
            "max_concurrent": self.max_concurrent_simulations,
        }

    def cancel_simulation(self, simulation_id: str) -> bool:
        """Cancel a running simulation"""

        if simulation_id not in self.simulations:
            return False

        instance = self.simulations[simulation_id]

        if instance.status == SimulationStatus.RUNNING:
            instance.status = SimulationStatus.CANCELLED
            instance.completed_at = datetime.now()

            # Cancel the future if it's still running
            if simulation_id in self.active_simulations:
                future = self.active_simulations[simulation_id]
                future.cancel()
                del self.active_simulations[simulation_id]

            return True

        return False

    def clear_completed_simulations(self):
        """Clear all completed simulations"""

        completed_ids = [
            sim_id
            for sim_id, sim in self.simulations.items()
            if sim.status
            in [
                SimulationStatus.COMPLETED,
                SimulationStatus.FAILED,
                SimulationStatus.CANCELLED,
            ]
        ]

        for sim_id in completed_ids:
            del self.simulations[sim_id]

        logger.info(f"Cleared {len(completed_ids)} completed simulations")

    def shutdown(self):
        """Shutdown the simulation engine"""

        self.running = False

        # Cancel all active simulations
        for sim_id in list(self.active_simulations.keys()):
            self.cancel_simulation(sim_id)

        # Shutdown executor
        self.executor.shutdown(wait=True)

        logger.info("Parallel simulation engine shutdown")


# Global simulation engine
parallel_simulation = ParallelSimulationEngine()
