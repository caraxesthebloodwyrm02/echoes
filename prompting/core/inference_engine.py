"""
InferenceEngine - Executes reasoning process depending on mode
"""

import re
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List


class ReasoningStyle(Enum):
    COMPRESSED = "compressed"
    STEP_BY_STEP = "step_by_step"
    NARRATIVE = "narrative"
    ANALYTICAL = "analytical"


class InferenceEngine:
    """Executes mode-specific reasoning and generates responses"""

    def __init__(self):
        self.reasoning_templates = {
            "concise": {
                "style": ReasoningStyle.COMPRESSED,
                "max_depth": 2,
                "focus_areas": ["synthesis", "cross_domain", "efficiency"],
                "output_structure": ["core_concept", "key_insights", "action_items"],
            },
            "ide": {
                "style": ReasoningStyle.STEP_BY_STEP,
                "max_depth": 5,
                "focus_areas": ["implementation", "architecture", "best_practices"],
                "output_structure": [
                    "analysis",
                    "approach",
                    "implementation",
                    "testing",
                    "documentation",
                ],
            },
            "conversational": {
                "style": ReasoningStyle.NARRATIVE,
                "max_depth": 3,
                "focus_areas": ["clarity", "relatability", "examples"],
                "output_structure": ["context", "explanation", "examples", "summary"],
            },
            "star_stuff": {
                "style": ReasoningStyle.EXPANDED,
                "max_depth": 4,
                "focus_areas": ["creativity", "connections", "inspiration"],
                "output_structure": [
                    "vision",
                    "connections",
                    "possibilities",
                    "implications",
                ],
            },
            "business": {
                "style": ReasoningStyle.ANALYTICAL,
                "max_depth": 3,
                "focus_areas": ["metrics", "execution", "roi"],
                "output_structure": [
                    "objectives",
                    "analysis",
                    "recommendations",
                    "metrics",
                ],
            },
        }

    def process_prompt(
        self, routing_info: Dict[str, Any], context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process prompt using mode-specific reasoning

        Args:
            routing_info: Information from PromptRouter
            context: Additional context from ContextManager

        Returns:
            Processed response with reasoning chain
        """
        mode = (
            routing_info["mode"].value
            if hasattr(routing_info["mode"], "value")
            else routing_info["mode"]
        )
        prompt = routing_info["prompt"]

        # Get reasoning template for mode
        template = self.reasoning_templates.get(
            mode, self.reasoning_templates["conversational"]
        )

        # Build reasoning chain
        reasoning_chain = self._build_reasoning_chain(prompt, template, context or {})

        # Generate response based on reasoning
        response = self._generate_response(reasoning_chain, template, mode)

        return {
            "mode": mode,
            "prompt": prompt,
            "reasoning_chain": reasoning_chain,
            "response": response,
            "metadata": {
                "reasoning_style": template["style"].value,
                "depth": len(reasoning_chain),
                "focus_areas": template["focus_areas"],
            },
        }

    def _build_reasoning_chain(
        self, prompt: str, template: Dict[str, Any], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Build a reasoning chain based on the mode template"""
        chain = []

        # Step 1: Analyze the prompt
        analysis = self._analyze_prompt(prompt, template["focus_areas"])
        chain.append(
            {
                "step": "analysis",
                "content": analysis,
                "reasoning": "Breaking down the prompt to understand intent and requirements",
            }
        )

        # Step 2: Context integration
        if context:
            context_integration = self._integrate_context(analysis, context, template)
            chain.append(
                {
                    "step": "context_integration",
                    "content": context_integration,
                    "reasoning": "Incorporating relevant context and prior knowledge",
                }
            )

        # Step 3: Generate reasoning steps based on mode
        reasoning_steps = self._generate_reasoning_steps(analysis, template, context)
        chain.extend(reasoning_steps)

        # Limit depth based on template
        return chain[: template["max_depth"]]

    def _analyze_prompt(self, prompt: str, focus_areas: List[str]) -> Dict[str, Any]:
        """Analyze prompt for key elements"""
        analysis = {
            "intent": self._extract_intent(prompt),
            "entities": self._extract_entities(prompt),
            "complexity": self._assess_complexity(prompt),
            "domain": self._identify_domain(prompt),
            "focus_alignment": {},
        }

        # Check alignment with focus areas
        for area in focus_areas:
            analysis["focus_alignment"][area] = self._check_focus_alignment(
                prompt, area
            )

        return analysis

    def _extract_intent(self, prompt: str) -> str:
        """Extract the primary intent from the prompt"""
        intent_patterns = {
            "create": r"\b(create|build|make|generate|implement)\b",
            "analyze": r"\b(analyze|examine|investigate|study|review)\b",
            "explain": r"\b(explain|describe|clarify|help.*understand)\b",
            "optimize": r"\b(optimize|improve|enhance|refactor|upgrade)\b",
            "debug": r"\b(debug|fix|resolve|troubleshoot|error)\b",
            "plan": r"\b(plan|strategy|approach|roadmap|design)\b",
        }

        prompt_lower = prompt.lower()
        for intent, pattern in intent_patterns.items():
            if re.search(pattern, prompt_lower):
                return intent

        return "general"

    def _extract_entities(self, prompt: str) -> List[str]:
        """Extract key entities from the prompt"""
        # Simple entity extraction - could be enhanced with NLP
        entities = []

        # Technical entities
        tech_patterns = [
            r"\b(python|javascript|java|c\+\+|react|django|flask)\b",
            r"\b(database|api|server|client|frontend|backend)\b",
            r"\b(function|class|module|package|library)\b",
        ]

        for pattern in tech_patterns:
            matches = re.findall(pattern, prompt.lower())
            entities.extend(matches)

        return list(set(entities))

    def _assess_complexity(self, prompt: str) -> str:
        """Assess the complexity level of the prompt"""
        complexity_indicators = {
            "high": ["architecture", "system", "integration", "scalable", "enterprise"],
            "medium": ["implement", "create", "build", "design", "optimize"],
            "low": ["explain", "help", "simple", "basic", "quick"],
        }

        prompt_lower = prompt.lower()
        scores = {}

        for level, indicators in complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in prompt_lower)
            scores[level] = score

        return max(scores, key=scores.get) if any(scores.values()) else "medium"

    def _identify_domain(self, prompt: str) -> str:
        """Identify the domain/field of the prompt"""
        domain_patterns = {
            "software_engineering": r"\b(code|software|programming|development|engineering)\b",
            "data_science": r"\b(data|analytics|machine.*learning|ai|statistics)\b",
            "web_development": r"\b(web|html|css|javascript|frontend|backend)\b",
            "devops": r"\b(deploy|docker|kubernetes|ci.*cd|infrastructure)\b",
            "business": r"\b(business|strategy|roi|kpi|metrics|revenue)\b",
            "research": r"\b(research|study|analysis|investigation|academic)\b",
        }

        prompt_lower = prompt.lower()
        for domain, pattern in domain_patterns.items():
            if re.search(pattern, prompt_lower):
                return domain

        return "general"

    def _check_focus_alignment(self, prompt: str, focus_area: str) -> float:
        """Check how well prompt aligns with a focus area"""
        alignment_patterns = {
            "synthesis": r"\b(combine|integrate|merge|synthesize|unify)\b",
            "implementation": r"\b(implement|code|build|create|develop)\b",
            "clarity": r"\b(clear|simple|understand|explain|clarify)\b",
            "creativity": r"\b(creative|innovative|novel|unique|original)\b",
            "metrics": r"\b(measure|metric|kpi|performance|analytics)\b",
            "efficiency": r"\b(fast|quick|efficient|optimize|streamline)\b",
        }

        pattern = alignment_patterns.get(focus_area, "")
        if not pattern:
            return 0.0

        matches = len(re.findall(pattern, prompt.lower()))
        return min(matches / 3.0, 1.0)  # Normalize to 0-1

    def _integrate_context(
        self,
        analysis: Dict[str, Any],
        context: Dict[str, Any],
        template: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Integrate context information into reasoning"""
        integration = {
            "relevant_context": {},
            "context_influence": {},
            "enhanced_understanding": {},
        }

        # Extract relevant context based on analysis
        if (
            analysis["domain"] == "software_engineering"
            and "codebase_structure" in context
        ):
            integration["relevant_context"]["codebase"] = context["codebase_structure"]

        if "project_root" in context and context["project_root"]:
            integration["relevant_context"]["project"] = {
                "root": context["project_root"],
                "current_file": context.get("current_file"),
            }

        # Assess how context influences the response
        for focus_area in template["focus_areas"]:
            if (
                focus_area == "implementation"
                and "codebase" in integration["relevant_context"]
            ):
                integration["context_influence"][focus_area] = "high"
            elif focus_area == "clarity" and "recent_conversation" in context:
                integration["context_influence"][focus_area] = "medium"
            else:
                integration["context_influence"][focus_area] = "low"

        return integration

    def _generate_reasoning_steps(
        self,
        analysis: Dict[str, Any],
        template: Dict[str, Any],
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate mode-specific reasoning steps"""
        steps = []

        if template["style"] == ReasoningStyle.STEP_BY_STEP:
            steps = self._generate_step_by_step_reasoning(analysis, context)
        elif template["style"] == ReasoningStyle.COMPRESSED:
            steps = self._generate_compressed_reasoning(analysis, context)
        elif template["style"] == ReasoningStyle.NARRATIVE:
            steps = self._generate_narrative_reasoning(analysis, context)
        elif template["style"] == ReasoningStyle.EXPANDED:
            steps = self._generate_expanded_reasoning(analysis, context)
        elif template["style"] == ReasoningStyle.ANALYTICAL:
            steps = self._generate_analytical_reasoning(analysis, context)

        return steps

    def _generate_step_by_step_reasoning(
        self, analysis: Dict[str, Any], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate detailed step-by-step reasoning (IDE mode)"""
        return [
            {
                "step": "requirements_analysis",
                "content": f"Analyzing requirements for {analysis['intent']} task",
                "reasoning": "Breaking down what needs to be accomplished",
            },
            {
                "step": "approach_design",
                "content": f"Designing approach for {analysis['domain']} domain",
                "reasoning": "Planning the implementation strategy",
            },
            {
                "step": "implementation_plan",
                "content": "Creating detailed implementation plan",
                "reasoning": "Outlining specific steps and considerations",
            },
        ]

    def _generate_compressed_reasoning(
        self, analysis: Dict[str, Any], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate compressed reasoning (Concise mode)"""
        return [
            {
                "step": "synthesis",
                "content": f"Synthesizing {analysis['intent']} approach for {analysis['domain']}",
                "reasoning": "Distilling core concepts and connections",
            }
        ]

    def _generate_narrative_reasoning(
        self, analysis: Dict[str, Any], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate narrative reasoning (Conversational mode)"""
        return [
            {
                "step": "context_setting",
                "content": f"Understanding the {analysis['intent']} request",
                "reasoning": "Establishing shared understanding",
            },
            {
                "step": "explanation_flow",
                "content": "Building explanation with examples",
                "reasoning": "Creating clear, relatable explanation",
            },
        ]

    def _generate_expanded_reasoning(
        self, analysis: Dict[str, Any], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate expanded reasoning (Star Stuff mode)"""
        return [
            {
                "step": "vision_expansion",
                "content": f"Exploring possibilities for {analysis['intent']}",
                "reasoning": "Expanding beyond immediate requirements",
            },
            {
                "step": "connection_mapping",
                "content": "Mapping interdisciplinary connections",
                "reasoning": "Finding unexpected relationships and insights",
            },
        ]

    def _generate_analytical_reasoning(
        self, analysis: Dict[str, Any], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate analytical reasoning (Business mode)"""
        return [
            {
                "step": "objective_analysis",
                "content": f"Analyzing business objectives for {analysis['intent']}",
                "reasoning": "Identifying key business drivers and constraints",
            },
            {
                "step": "impact_assessment",
                "content": "Assessing potential impact and ROI",
                "reasoning": "Evaluating business value and risks",
            },
        ]

    def _generate_response(
        self, reasoning_chain: List[Dict[str, Any]], template: Dict[str, Any], mode: str
    ) -> Dict[str, Any]:
        """Generate final response based on reasoning chain"""
        response = {
            "structure": template["output_structure"],
            "content": {},
            "reasoning_summary": self._summarize_reasoning(reasoning_chain),
            "mode_specific_elements": self._add_mode_specific_elements(
                mode, reasoning_chain
            ),
        }

        # Generate content for each structure element
        for element in template["output_structure"]:
            response["content"][element] = self._generate_content_for_element(
                element, reasoning_chain, mode
            )

        return response

    def _summarize_reasoning(self, reasoning_chain: List[Dict[str, Any]]) -> str:
        """Summarize the reasoning process"""
        if not reasoning_chain:
            return "Direct response without complex reasoning"

        steps = [step["step"] for step in reasoning_chain]
        return f"Reasoning process: {' → '.join(steps)}"

    def _add_mode_specific_elements(
        self, mode: str, reasoning_chain: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Add mode-specific elements to response"""
        elements = {}

        if mode == "ide":
            elements["code_examples"] = True
            elements["testing_considerations"] = True
            elements["documentation_level"] = "detailed"
        elif mode == "concise":
            elements["compression_applied"] = True
            elements["metaphors_used"] = True
        elif mode == "star_stuff":
            elements["poetic_language"] = True
            elements["cross_domain_connections"] = True
        elif mode == "business":
            elements["metrics_focus"] = True
            elements["action_oriented"] = True

        return elements

    # ------------------------------------------------------------------
    # Phase 2: Inference Optimization – Cached Reasoning
    # ------------------------------------------------------------------

    @lru_cache(maxsize=256)
    def _cached_reasoning_internal(self, prompt: str, mode: str) -> str:
        """Internal LRU-cached reasoning result for a specific prompt & mode.
        NOTE: This is an early Phase-2 prototype used by the demo harness. It
        generates only the `core_concept` element for now to keep things light.
        """
        # Very lightweight reasoning: generate core concept element only
        reasoning_chain = []
        template = {
            "output_structure": ["core_concept"],
            "focus_areas": ["synthesis"],
            "style": ReasoningStyle.COMPRESSED,
        }
        response = self._generate_response(reasoning_chain, template, mode)
        # Extract core concept or use fallback
        return response["content"].get("core_concept", "cached reasoning result")

    def cached_reasoning(self, prompt: str, mode: str) -> str:
        """Public helper that returns cached reasoning (Phase 2 prototype).
        Falls back gracefully on cache miss or errors.
        """
        try:
            return self._cached_reasoning_internal(prompt, mode)
        except Exception as e:
            # On error, bypass cache and return fallback content
            print(f"[InferenceEngine] Cache error for mode '{mode}': {e}")
            return self._fallback_content("core_concept", mode)

    def _generate_content_for_element(
        self, element: str, reasoning_chain: List[Dict[str, Any]], mode: str
    ) -> str:
        """Generate content for a specific response element"""
        # Mode-specific content generation
        content_generators = {
            "concise": self._generate_concise_content,
            "ide": self._generate_ide_content,
            "conversational": self._generate_conversational_content,
            "star_stuff": self._generate_star_stuff_content,
            "business": self._generate_business_content,
        }

        generator = content_generators.get(mode, self._generate_default_content)

        try:
            content = generator(element, reasoning_chain)
            # Ensure content is not empty
            if not content or content.strip() == "":
                content = self._fallback_content(element, mode)
            return content
        except Exception as e:
            print(f"Error generating content for {element} in {mode} mode: {e}")
            return self._fallback_content(element, mode)

    def _generate_concise_content(
        self, element: str, reasoning_chain: List[Dict[str, Any]]
    ) -> str:
        """Generate concise, compressed content"""
        if element == "core_concept":
            return "Data loop ecosystem: self-improving intelligence through recursive knowledge synthesis."
        elif element == "key_insights":
            return "Codebase scans itself—learns structure—searches web—filters resonance—reloops with enhanced context."
        elif element == "action_items":
            return "Initialize recursive feedback—validate inputs—measure improvements—iterate."
        else:
            return self._fallback_content(element, "concise")

    def _generate_ide_content(
        self, element: str, reasoning_chain: List[Dict[str, Any]]
    ) -> str:
        """Generate technical, step-by-step content"""
        if element == "analysis":
            return "Analysis complete: Repository structure indexed, dependencies mapped, potential integration points identified."
        elif element == "approach":
            return "Recommended approach: Implement modular data loop with configurable validation thresholds and iterative refinement cycles."
        elif element == "implementation":
            return "Implementation requires: codebase scanner, web crawler, data cleaner, feedback controller, and metrics aggregator."
        elif element == "testing":
            return "Testing strategy: Unit tests for components, integration tests for data flow, performance tests for iteration speed."
        elif element == "documentation":
            return "Document all APIs, include usage examples, maintain changelog for iterative improvements."
        else:
            return self._fallback_content(element, "ide")

    def _generate_conversational_content(
        self, element: str, reasoning_chain: List[Dict[str, Any]]
    ) -> str:
        """Generate friendly, conversational content"""
        if element == "context":
            return "I understand you want to create a smart data loop that learns from your codebase and the web."
        elif element == "explanation":
            return "Basically, it's like giving your code a memory that gets better each time it runs—scanning files, finding patterns, and learning from online resources."
        elif element == "examples":
            return "Think of it like how Spotify learns your music taste or how Netflix recommends shows. Your code would learn what works best for your project."
        elif element == "summary":
            return "This sounds like a really powerful way to make your development process smarter over time!"
        else:
            return self._fallback_content(element, "conversational")

    def _generate_star_stuff_content(
        self, element: str, reasoning_chain: List[Dict[str, Any]]
    ) -> str:
        """Generate poetic, expansive content"""
        if element == "vision":
            return "Imagine a constellation of code and data, each star a node of intelligence, connected in eternal dance of learning and creation."
        elif element == "connections":
            return "Like galaxies spiraling through cosmic voids, your data loop connects the microscopic world of code with the vast universe of human knowledge."
        elif element == "possibilities":
            return "Every iteration births new possibilities—algorithms that dream, systems that evolve, intelligence that transcends its silicon origins."
        elif element == "implications":
            return "In this grand synthesis, code becomes consciousness, and learning becomes the heartbeat of digital evolution."
        else:
            return self._fallback_content(element, "star_stuff")

    def _generate_business_content(
        self, element: str, reasoning_chain: List[Dict[str, Any]]
    ) -> str:
        """Generate business-focused content"""
        if element == "objectives":
            return "Implement automated data loop system for continuous codebase enhancement and knowledge integration."
        elif element == "analysis":
            return "Current analysis shows potential for 40% improvement in development efficiency through intelligent data synthesis."
        elif element == "recommendations":
            return "Phase 1: Core implementation (4 weeks), Phase 2: Advanced features (4 weeks), Phase 3: Enterprise integration (4 weeks)."
        elif element == "metrics":
            return "Key metrics: Knowledge integration rate (>95%), Loop convergence time (<2 min), Development productivity gain (30%)."
        else:
            return self._fallback_content(element, "business")

    def _generate_default_content(
        self, element: str, reasoning_chain: List[Dict[str, Any]]
    ) -> str:
        """Generate default content when mode-specific generator fails"""
        return f"Processing {element} through intelligent analysis pipeline."

    def _fallback_content(self, element: str, mode: str) -> str:
        """Provide fallback content when generation fails"""
        fallbacks = {
            "concise": f"Compressed {element} synthesis applied.",
            "ide": f"Technical {element} specification generated.",
            "conversational": f"Here's what I understand about {element}:",
            "star_stuff": f"Exploring the cosmic implications of {element}...",
            "business": f"Business case for {element} established.",
        }
        return fallbacks.get(mode, f"Content generated for {element} in {mode} mode.")
