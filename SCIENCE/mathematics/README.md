# Mathematics in CI/CD: Algorithms, Graphs, and Optimization

## Graph Theory in Dependency Management

### Dependency Graphs and Topological Sorting
**Principle**: Directed acyclic graphs (DAGs) model build dependencies.

**CI/CD Application**:
```python
from typing import Dict, List, Set
from collections import defaultdict, deque

class DependencyGraph:
    def __init__(self):
        self.graph = defaultdict(list)  # Adjacency list
        self.in_degree = defaultdict(int)  # In-degree count
        self.nodes = set()

    def add_dependency(self, dependent: str, dependency: str):
        """Add a dependency relationship: dependent -> dependency"""
        self.graph[dependency].append(dependent)
        self.in_degree[dependent] += 1
        self.nodes.add(dependent)
        self.nodes.add(dependency)

    def topological_sort(self) -> List[str]:
        """Perform topological sort using Kahn's algorithm"""
        result = []
        queue = deque()

        # Start with nodes that have no dependencies
        for node in self.nodes:
            if self.in_degree[node] == 0:
                queue.append(node)

        while queue:
            current = queue.popleft()
            result.append(current)

            # Remove edges from current node
            for neighbor in self.graph[current]:
                self.in_degree[neighbor] -= 1
                if self.in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(result) != len(self.nodes):
            raise ValueError("Dependency graph contains cycles")

        return result

    def get_build_order(self) -> List[str]:
        """Get the optimal build order for CI/CD pipeline"""
        return self.topological_sort()
```

### Critical Path Analysis in Pipeline Optimization
```python
import networkx as nx  # Requires networkx

class PipelineCriticalPath:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_stage(self, stage_name: str, duration: float, dependencies: List[str] = None):
        """Add a pipeline stage with duration and dependencies"""
        self.graph.add_node(stage_name, duration=duration)
        if dependencies:
            for dep in dependencies:
                self.graph.add_edge(dep, stage_name)

    def calculate_critical_path(self) -> Dict:
        """Calculate critical path using longest path algorithm"""
        # Calculate earliest start times
        earliest_start = {}
        for node in nx.topological_sort(self.graph):
            predecessors = list(self.graph.predecessors(node))
            if not predecessors:
                earliest_start[node] = 0
            else:
                earliest_start[node] = max(
                    earliest_start[pred] + self.graph.nodes[pred]['duration']
                    for pred in predecessors
                )

        # Calculate latest start times
        latest_start = {}
        for node in reversed(list(nx.topological_sort(self.graph))):
            successors = list(self.graph.successors(node))
            if not successors:
                latest_start[node] = earliest_start[node]
            else:
                latest_start[node] = min(
                    latest_start[succ] - self.graph.nodes[node]['duration']
                    for succ in successors
                )

        # Identify critical path
        critical_path = [
            node for node in self.graph.nodes()
            if earliest_start[node] == latest_start[node]
        ]

        total_duration = max(earliest_start.values()) + max(
            self.graph.nodes[node]['duration'] for node in critical_path
        )

        return {
            "critical_path": critical_path,
            "total_duration": total_duration,
            "bottlenecks": [node for node in critical_path if self.graph.nodes[node]['duration'] > 10]
        }
```

## Set Theory in Configuration Management

### Feature Flags and Configuration Sets
```python
class FeatureFlagSet:
    def __init__(self):
        self.enabled_features = set()
        self.all_features = set()
        self.user_segments = defaultdict(set)

    def enable_feature(self, feature: str, users: Set[str] = None):
        """Enable a feature for specific users or globally"""
        self.all_features.add(feature)
        if users is None:
            self.enabled_features.add(feature)
        else:
            self.user_segments[feature].update(users)

    def is_feature_enabled(self, feature: str, user: str = None) -> bool:
        """Check if feature is enabled for user or globally"""
        if feature in self.enabled_features:
            return True
        if user and user in self.user_segments[feature]:
            return True
        return False

    def get_feature_intersection(self, feature_a: str, feature_b: str) -> Set[str]:
        """Get users who have both features enabled"""
        users_a = self.user_segments[feature_a]
        users_b = self.user_segments[feature_b]
        global_enabled = {feature_a, feature_b}.issubset(self.enabled_features)

        if global_enabled:
            return self.user_segments[feature_a] | self.user_segments[feature_b]
        else:
            return users_a & users_b
```

## Probability and Statistics in Risk Assessment

### Bayesian Inference for Deployment Success
```python
import math

class DeploymentRiskAssessor:
    def __init__(self):
        self.prior_success = 0.8  # Prior belief in deployment success
        self.evidence_history = []

    def update_belief(self, success: bool, confidence: float = 1.0):
        """Update success probability using Bayesian inference"""
        likelihood = confidence if success else (1 - confidence)

        # Bayesian update
        posterior = (self.prior_success * likelihood) / (
            self.prior_success * likelihood + (1 - self.prior_success) * (1 - likelihood)
        )

        self.prior_success = posterior
        self.evidence_history.append((success, confidence))

        return posterior

    def predict_failure_probability(self, risk_factors: Dict[str, float]) -> float:
        """Predict deployment failure using logistic regression"""
        # Simplified risk model
        base_risk = 1 - self.prior_success
        risk_multiplier = 1.0

        for factor, weight in risk_factors.items():
            if factor == "complexity":
                risk_multiplier *= (1 + weight * 0.1)
            elif factor == "test_coverage":
                risk_multiplier *= max(0.1, 1 - weight)
            elif factor == "review_count":
                risk_multiplier *= max(0.5, 1 / (weight + 1))

        return min(1.0, base_risk * risk_multiplier)

    def get_confidence_interval(self, confidence_level: float = 0.95) -> tuple:
        """Calculate confidence interval for success probability"""
        n = len(self.evidence_history)
        if n < 2:
            return (self.prior_success, self.prior_success)

        # Simplified confidence interval calculation
        variance = self.prior_success * (1 - self.prior_success) / n
        z_score = 1.96  # 95% confidence
        margin = z_score * math.sqrt(variance)

        return (max(0, self.prior_success - margin), min(1, self.prior_success + margin))
```

## Optimization Theory in Resource Allocation

### Linear Programming for CI/CD Resource Optimization
```python
from typing import List, Tuple
import numpy as np

class ResourceOptimizer:
    def __init__(self):
        self.resources = []  # Available resources
        self.requirements = []  # Pipeline requirements
        self.costs = []  # Resource costs

    def add_resource(self, name: str, capacity: float, cost_per_unit: float):
        """Add a resource to the optimization problem"""
        self.resources.append((name, capacity, cost_per_unit))

    def add_pipeline(self, name: str, resource_requirements: Dict[str, float], priority: float):
        """Add a pipeline with its resource requirements"""
        self.requirements.append((name, resource_requirements, priority))

    def optimize_allocation(self) -> Dict[str, Dict[str, float]]:
        """Solve the resource allocation optimization problem"""
        # Simplified greedy optimization
        allocation = defaultdict(dict)
        remaining_capacity = {r[0]: r[1] for r in self.resources}

        # Sort pipelines by priority
        sorted_pipelines = sorted(self.requirements, key=lambda x: x[2], reverse=True)

        for pipeline_name, requirements, priority in sorted_pipelines:
            for resource_name, required_amount in requirements.items():
                if resource_name in remaining_capacity:
                    allocated = min(required_amount, remaining_capacity[resource_name])
                    allocation[pipeline_name][resource_name] = allocated
                    remaining_capacity[resource_name] -= allocated

        return dict(allocation)

    def calculate_efficiency(self, allocation: Dict) -> float:
        """Calculate resource utilization efficiency"""
        total_allocated = sum(sum(pipeline.values()) for pipeline in allocation.values())
        total_capacity = sum(r[1] for r in self.resources)

        return total_allocated / total_capacity if total_capacity > 0 else 0
```

## Information Theory in Data Compression

### Entropy-Based Log Analysis
```python
import math
from collections import Counter

class LogEntropyAnalyzer:
    def __init__(self):
        self.log_entries = []

    def add_log_entry(self, entry: str):
        """Add a log entry for entropy analysis"""
        self.log_entries.append(entry)

    def calculate_entropy(self) -> float:
        """Calculate Shannon entropy of log patterns"""
        if not self.log_entries:
            return 0.0

        # Count frequency of each log pattern
        pattern_counts = Counter(self.log_entries)
        total_entries = len(self.log_entries)

        entropy = 0.0
        for count in pattern_counts.values():
            probability = count / total_entries
            entropy -= probability * math.log2(probability)

        return entropy

    def detect_anomalies(self, threshold: float = 2.0) -> List[str]:
        """Detect anomalous log patterns using entropy"""
        if len(self.log_entries) < 10:
            return []

        recent_entries = self.log_entries[-100:]  # Last 100 entries
        baseline_entropy = self.calculate_entropy()

        # Calculate entropy of recent entries
        recent_counts = Counter(recent_entries)
        recent_entropy = 0.0
        for count in recent_counts.values():
            probability = count / len(recent_entries)
            recent_entropy -= probability * math.log2(probability)

        # Check for significant entropy changes (potential anomalies)
        entropy_diff = abs(recent_entropy - baseline_entropy)

        if entropy_diff > threshold:
            # Find unusual patterns
            all_patterns = Counter(self.log_entries)
            recent_patterns = set(recent_counts.keys())

            anomalies = []
            for pattern in recent_patterns:
                if pattern not in all_patterns or recent_counts[pattern] > all_patterns[pattern] * 2:
                    anomalies.append(pattern)

            return anomalies

        return []
```

## Practical Applications

### Pipeline Dependency Resolution
```python
def resolve_pipeline_dependencies(services: Dict[str, List[str]]) -> List[str]:
    """
    Resolve service startup dependencies using topological sort

    Args:
        services: Dict mapping service names to their dependencies

    Returns:
        Ordered list of services for startup
    """
    graph = DependencyGraph()

    for service, deps in services.items():
        for dep in deps:
            graph.add_dependency(service, dep)

    try:
        return graph.get_build_order()
    except ValueError as e:
        print(f"Dependency cycle detected: {e}")
        return []

# Example usage
services = {
    "api_gateway": ["auth_service"],
    "user_service": ["database", "cache"],
    "auth_service": ["database", "redis"],
    "database": [],
    "cache": [],
    "redis": []
}

startup_order = resolve_pipeline_dependencies(services)
print("Service startup order:", startup_order)
```

## Key Takeaways

1. **Graphs Model Dependencies**: Use topological sorting for build order
2. **Sets Manage Configurations**: Feature flags and user segmentation
3. **Probability Assesses Risk**: Bayesian updates for deployment success
4. **Optimization Allocates Resources**: Linear programming for efficiency
5. **Information Theory Detects Anomalies**: Entropy analysis for log monitoring

## References

- "Graph Algorithms in Software Engineering" - ACM Computing Surveys
- "Probabilistic Risk Assessment in DevOps" - IEEE Software
- "Optimization Methods for CI/CD Pipelines" - Journal of Systems and Software
