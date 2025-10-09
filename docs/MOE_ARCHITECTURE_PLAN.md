# Mixture of Experts (MoE) Architecture - Implementation Plan

## Overview

Implement a dynamic Mixture of Experts system where specialized models/experts handle different aspects of queries, coordinated by an intelligent router.

## Architecture

```
                     ┌──────────────┐
                     │  User Query  │
                     └──────┬───────┘
                            ↓
              ┌─────────────────────────┐
              │   Gating Network        │
              │  (Router/Classifier)    │
              └─────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                   ↓                   ↓
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│Coding Expert  │  │Reasoning Expert│  │Planning Expert│
│ (Qwen/DeepSeek│  │   (QwQ/R1)    │  │  (Mistral)    │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                   │                   │
        └───────────────────┴───────────────────┘
                            ↓
              ┌─────────────────────────┐
              │    Aggregator           │
              │  (Combines Responses)   │
              └─────────────────────────┘
```

## 1. Expert Definitions

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ExpertCapability:
    """Expert capability definition."""
    name: str
    confidence_threshold: float
    max_load: int
    average_latency_ms: float

class Expert(ABC):
    """Base expert class."""

    def __init__(self, name: str):
        self.name = name
        self.capabilities: List[ExpertCapability] = []
        self.current_load = 0
        self.total_queries = 0
        self.success_rate = 1.0

    @abstractmethod
    async def can_handle(self, query: Query) -> float:
        """Return confidence score (0-1) for handling query."""
        pass

    @abstractmethod
    async def process(self, query: Query) -> Response:
        """Process query and return response."""
        pass

    def update_stats(self, success: bool, latency: float):
        """Update expert statistics."""
        self.total_queries += 1
        if success:
            self.success_rate = (
                (self.success_rate * (self.total_queries - 1) + 1)
                / self.total_queries
            )
        else:
            self.success_rate = (
                (self.success_rate * (self.total_queries - 1))
                / self.total_queries
            )

class CodingExpert(Expert):
    """Expert for coding tasks."""

    def __init__(self):
        super().__init__("CodingExpert")
        self.models = [
            "qwen-coder",
            "deepseek-coder",
            "qwen-coder-local",
        ]
        self.capabilities = [
            ExpertCapability("code_generation", 0.9, 10, 500),
            ExpertCapability("code_review", 0.85, 10, 400),
            ExpertCapability("debugging", 0.88, 10, 600),
            ExpertCapability("refactoring", 0.87, 10, 550),
        ]

    async def can_handle(self, query: Query) -> float:
        """Score coding-related queries."""
        keywords = [
            "write", "code", "function", "class", "implement",
            "debug", "fix", "error", "refactor", "optimize",
        ]

        score = 0.0
        query_lower = query.text.lower()

        for keyword in keywords:
            if keyword in query_lower:
                score += 0.15

        # Check for code snippets
        if "```" in query.text or "def " in query.text:
            score += 0.3

        return min(score, 1.0)

    async def process(self, query: Query) -> Response:
        """Process coding query."""
        # Select best model based on load
        model = self._select_model()

        # Route to model
        from app.core import create_agentic_assistant
        assistant = create_agentic_assistant(model_id=model)

        response_text = assistant.chat(query.text)

        return Response(
            text=response_text,
            expert=self.name,
            model=model,
            confidence=await self.can_handle(query),
        )

class ReasoningExpert(Expert):
    """Expert for complex reasoning."""

    def __init__(self):
        super().__init__("ReasoningExpert")
        self.models = [
            "qwq-32b",
            "deepseek-r1-local",
            "mistral-large",
        ]
        self.capabilities = [
            ExpertCapability("problem_solving", 0.95, 5, 1200),
            ExpertCapability("analysis", 0.92, 8, 900),
            ExpertCapability("explanation", 0.90, 10, 700),
        ]

    async def can_handle(self, query: Query) -> float:
        """Score reasoning queries."""
        indicators = [
            "why", "how", "explain", "analyze", "reason",
            "compare", "evaluate", "assess", "understand",
            "what if", "trade-off", "pros and cons",
        ]

        score = 0.0
        query_lower = query.text.lower()

        for indicator in indicators:
            if indicator in query_lower:
                score += 0.12

        # Complex questions get higher score
        if len(query.text.split()) > 20:
            score += 0.2

        return min(score, 1.0)

class KnowledgeExpert(Expert):
    """Expert using knowledge graph."""

    def __init__(self, knowledge_graph):
        super().__init__("KnowledgeExpert")
        self.kg = knowledge_graph
        self.capabilities = [
            ExpertCapability("codebase_query", 0.92, 20, 200),
            ExpertCapability("context_retrieval", 0.90, 20, 150),
        ]

    async def can_handle(self, query: Query) -> float:
        """Score knowledge-based queries."""
        indicators = [
            "find", "where", "what does", "how does",
            "show me", "list", "search", "locate",
        ]

        score = 0.0
        for indicator in indicators:
            if indicator in query.text.lower():
                score += 0.15

        return min(score, 1.0)

    async def process(self, query: Query) -> Response:
        """Query knowledge graph."""
        results = await self.kg.query_semantic(query.text)

        # Format results
        formatted = self._format_results(results)

        return Response(
            text=formatted,
            expert=self.name,
            metadata={"results": results},
        )
```

## 2. Gating Network (Router)

```python
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel

class GatingNetwork(nn.Module):
    """
    Neural gating network for expert selection.
    """

    def __init__(self, num_experts: int, hidden_size: int = 768):
        super().__init__()

        # Use pre-trained encoder
        self.encoder = AutoModel.from_pretrained("microsoft/codebert-base")
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")

        # Gating layers
        self.gate = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, num_experts),
            nn.Softmax(dim=-1),
        )

    def forward(self, query_text: str) -> torch.Tensor:
        """Return expert selection probabilities."""
        # Encode query
        inputs = self.tokenizer(
            query_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
        )

        with torch.no_grad():
            outputs = self.encoder(**inputs)

        # Pool embeddings
        embeddings = outputs.last_hidden_state.mean(dim=1)

        # Gate
        expert_probs = self.gate(embeddings)

        return expert_probs

class MoERouter:
    """
    Intelligent router for expert selection.
    """

    def __init__(self, experts: List[Expert]):
        self.experts = {e.name: e for e in experts}
        self.gating_network = GatingNetwork(len(experts))
        self.query_classifier = QueryClassifier()

    async def route(
        self,
        query: Query,
        top_k: int = 1,
    ) -> List[Tuple[Expert, float]]:
        """
        Route query to best expert(s).

        Returns:
            List of (expert, confidence) tuples
        """
        # Get expert confidence scores
        scores = {}

        # 1. Neural gating network
        with torch.no_grad():
            gate_probs = self.gating_network(query.text)

        for idx, expert in enumerate(self.experts.values()):
            scores[expert.name] = float(gate_probs[0, idx])

        # 2. Expert self-assessment
        for expert in self.experts.values():
            self_score = await expert.can_handle(query)
            # Combine with gate score
            scores[expert.name] = (
                0.6 * scores[expert.name] +
                0.4 * self_score
            )

        # 3. Adjust for load balancing
        for expert_name in scores:
            expert = self.experts[expert_name]
            if expert.current_load >= max(e.capabilities[0].max_load
                                          for e in [expert]):
                scores[expert_name] *= 0.5  # Penalize overloaded

        # Select top-k experts
        sorted_experts = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:top_k]

        return [
            (self.experts[name], score)
            for name, score in sorted_experts
        ]
```

## 3. Response Aggregation

```python
class ResponseAggregator:
    """
    Aggregate responses from multiple experts.
    """

    def __init__(self):
        self.strategies = {
            "voting": self._voting_aggregation,
            "weighted": self._weighted_aggregation,
            "sequential": self._sequential_aggregation,
            "ensemble": self._ensemble_aggregation,
        }

    async def aggregate(
        self,
        responses: List[Tuple[Response, float]],
        strategy: str = "weighted",
    ) -> Response:
        """Aggregate multiple responses."""
        aggregator = self.strategies.get(strategy, self._weighted_aggregation)
        return await aggregator(responses)

    async def _weighted_aggregation(
        self,
        responses: List[Tuple[Response, float]],
    ) -> Response:
        """Weight responses by confidence."""
        # For text responses, select highest confidence
        best_response, best_score = max(responses, key=lambda x: x[1])

        # Add metadata about other responses
        best_response.metadata["alternative_responses"] = [
            {
                "expert": r.expert,
                "confidence": score,
                "summary": r.text[:100],
            }
            for r, score in responses if r != best_response
        ]

        return best_response

    async def _ensemble_aggregation(
        self,
        responses: List[Tuple[Response, float]],
    ) -> Response:
        """Combine insights from all responses."""
        # Use another model to synthesize
        combined_text = "\n\n".join([
            f"**{r.expert} (confidence: {score:.2f}):**\n{r.text}"
            for r, score in responses
        ])

        synthesis_prompt = f"""
        Multiple experts provided these responses:

        {combined_text}

        Synthesize a comprehensive answer combining the best insights.
        """

        # Use reasoning model for synthesis
        from app.core import create_agentic_assistant
        assistant = create_agentic_assistant(model_id="qwq-32b")

        final_text = assistant.chat(synthesis_prompt)

        return Response(
            text=final_text,
            expert="Ensemble",
            metadata={"source_responses": responses},
        )
```

## 4. Dynamic Expert Management

```python
class ExpertManager:
    """
    Manage expert lifecycle and performance.
    """

    def __init__(self):
        self.experts: Dict[str, Expert] = {}
        self.performance_tracker = PerformanceTracker()

    def register_expert(self, expert: Expert):
        """Register new expert."""
        self.experts[expert.name] = expert

    def remove_expert(self, expert_name: str):
        """Remove underperforming expert."""
        if expert_name in self.experts:
            del self.experts[expert_name]

    async def evaluate_experts(self):
        """Evaluate and rank experts."""
        rankings = {}

        for name, expert in self.experts.items():
            # Calculate score based on:
            # - Success rate
            # - Average latency
            # - Load capacity
            score = (
                0.5 * expert.success_rate +
                0.3 * (1 - expert.current_load / expert.capabilities[0].max_load) +
                0.2 * (1 / (expert.capabilities[0].average_latency_ms / 1000))
            )
            rankings[name] = score

        return rankings

    async def scale_experts(self):
        """Dynamically scale expert instances."""
        rankings = await self.evaluate_experts()

        # Add instances for high-performing, overloaded experts
        for name, score in rankings.items():
            expert = self.experts[name]
            if (expert.current_load > expert.capabilities[0].max_load * 0.8
                and score > 0.8):
                # Spawn additional instance
                await self._spawn_expert_instance(expert)
```

## Implementation Timeline

### Week 1-2: Expert Framework
- [ ] Base expert classes
- [ ] Expert implementations (7+ experts)
- [ ] Expert registration
- [ ] Performance tracking

### Week 3-4: Gating Network
- [ ] Neural router implementation
- [ ] Query classifier
- [ ] Load balancing
- [ ] Confidence scoring

### Week 5-6: Aggregation
- [ ] Response aggregators
- [ ] Ensemble methods
- [ ] Conflict resolution
- [ ] Quality assurance

### Week 7-8: Dynamic Management
- [ ] Expert scaling
- [ ] Performance monitoring
- [ ] Auto-optimization
- [ ] A/B testing

## Success Metrics

- **Routing Accuracy**: >95%
- **Response Quality**: >90% user satisfaction
- **Latency**: <300ms routing overhead
- **Load Balance**: <20% variance across experts
- **Scalability**: Linear scaling to 20+ experts

## Configuration

```yaml
moe:
  enabled: true

  router:
    type: neural  # or heuristic
    model: microsoft/codebert-base
    top_k: 1  # Number of experts to use
    min_confidence: 0.7

  aggregation:
    strategy: weighted  # weighted, voting, ensemble
    synthesis_model: qwq-32b

  experts:
    - name: CodingExpert
      models: [qwen-coder, deepseek-coder]
      max_instances: 3
    - name: ReasoningExpert
      models: [qwq-32b, deepseek-r1-local]
      max_instances: 2

  management:
    auto_scale: true
    performance_threshold: 0.85
    remove_underperforming: false
```

## Next Steps

1. Implement base expert framework
2. Create 7+ specialized experts
3. Build gating network
4. Implement aggregation strategies
5. Add performance monitoring
