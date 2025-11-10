#!/usr/bin/env python3
"""
Resilience Manager - Comprehensive System Resilience Tools
Based on 18-hour optimization experience

Features:
- Circuit breaker implementation
- Third-party dependency management
- Interruption prevention
- Health monitoring
- Performance optimization
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import hashlib

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    expected_exception: type = Exception
    success_threshold: int = 3

@dataclass
class DependencyConfig:
    name: str
    timeout: float = 10.0
    retry_attempts: int = 3
    retry_delay: float = 1.0
    circuit_breaker_config: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)

class CircuitBreaker:
    """Advanced circuit breaker implementation"""

    def __init__(self, config: CircuitBreakerConfig = None):
        self.config = config or CircuitBreakerConfig()
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.success_count = 0
        self.logger = logging.getLogger(__name__)

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.config.recovery_timeout
        )

    def _on_success(self):
        """Handle successful execution"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._reset()
        else:
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            self.logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

    def _reset(self):
        """Reset circuit breaker to closed state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.logger.info("Circuit breaker reset to CLOSED state")

class DependencyManager:
    """Manages third-party dependencies with resilience"""

    def __init__(self):
        self.dependencies: Dict[str, DependencyConfig] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.health_status: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)

    def register_dependency(self, config: DependencyConfig):
        """Register a third-party dependency"""
        self.dependencies[config.name] = config
        self.circuit_breakers[config.name] = CircuitBreaker(config.circuit_breaker_config)
        self.health_status[config.name] = {
            "status": "unknown",
            "last_check": None,
            "response_time": 0.0,
            "error_count": 0
        }
        self.logger.info(f"Registered dependency: {config.name}")

    async def call_dependency(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """Call a dependency with resilience protection"""
        if name not in self.dependencies:
            raise ValueError(f"Dependency {name} not registered")

        config = self.dependencies[name]
        circuit_breaker = self.circuit_breakers[name]

        start_time = time.time()

        try:
            # Apply timeout
            result = await asyncio.wait_for(
                circuit_breaker.execute(func, *args, **kwargs),
                timeout=config.timeout
            )

            # Update health status
            response_time = time.time() - start_time
            self.health_status[name].update({
                "status": "healthy",
                "last_check": datetime.now(),
                "response_time": response_time,
                "error_count": 0
            })

            return result

        except asyncio.TimeoutError:
            self.health_status[name]["error_count"] += 1
            self.health_status[name]["status"] = "timeout"
            raise Exception(f"Dependency {name} timed out after {config.timeout}s")

        except Exception as e:
            self.health_status[name]["error_count"] += 1
            self.health_status[name]["status"] = "error"
            self.logger.error(f"Dependency {name} failed: {e}")
            raise

    async def check_dependency_health(self, name: str) -> Dict[str, Any]:
        """Check health of a specific dependency"""
        if name not in self.health_status:
            return {"status": "not_found"}

        return self.health_status[name].copy()

    async def check_all_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all dependencies"""
        return {name: status.copy() for name, status in self.health_status.items()}

class InterruptionPreventer:
    """Prevents system interruptions through proactive monitoring"""

    def __init__(self):
        self.monitored_services: Dict[str, Dict[str, Any]] = {}
        self.fallback_strategies: Dict[str, Callable] = {}
        self.alert_thresholds: Dict[str, Dict[str, float]] = {}
        self.logger = logging.getLogger(__name__)

    def monitor_service(self, name: str, health_check: Callable,
                       fallback_strategy: Callable = None,
                       alert_thresholds: Dict[str, float] = None):
        """Monitor a service for potential interruptions"""
        self.monitored_services[name] = {
            "health_check": health_check,
            "last_check": None,
            "status": "unknown",
            "consecutive_failures": 0
        }

        if fallback_strategy:
            self.fallback_strategies[name] = fallback_strategy

        if alert_thresholds:
            self.alert_thresholds[name] = alert_thresholds

        self.logger.info(f"Started monitoring service: {name}")

    async def check_service_health(self, name: str) -> Dict[str, Any]:
        """Check health of a monitored service"""
        if name not in self.monitored_services:
            return {"status": "not_monitored"}

        service = self.monitored_services[name]

        try:
            result = await service["health_check"]() if asyncio.iscoroutinefunction(service["health_check"]) else service["health_check"]()

            service["last_check"] = datetime.now()
            service["status"] = "healthy"
            service["consecutive_failures"] = 0

            return {
                "status": "healthy",
                "last_check": service["last_check"],
                "data": result
            }

        except Exception as e:
            service["consecutive_failures"] += 1
            service["last_check"] = datetime.now()
            service["status"] = "unhealthy"

            self.logger.error(f"Service {name} health check failed: {e}")

            # Check if we should trigger fallback
            if self._should_trigger_fallback(name):
                await self._trigger_fallback(name)

            return {
                "status": "unhealthy",
                "last_check": service["last_check"],
                "consecutive_failures": service["consecutive_failures"],
                "error": str(e)
            }

    def _should_trigger_fallback(self, name: str) -> bool:
        """Check if fallback strategy should be triggered"""
        service = self.monitored_services[name]
        thresholds = self.alert_thresholds.get(name, {})

        # Default threshold: 3 consecutive failures
        max_failures = thresholds.get("max_consecutive_failures", 3)
        return service["consecutive_failures"] >= max_failures

    async def _trigger_fallback(self, name: str):
        """Trigger fallback strategy for a service"""
        if name in self.fallback_strategies:
            try:
                await self.fallback_strategies[name]() if asyncio.iscoroutinefunction(self.fallback_strategies[name]) else self.fallback_strategies[name]()
                self.logger.info(f"Fallback strategy triggered for service: {name}")
            except Exception as e:
                self.logger.error(f"Fallback strategy failed for {name}: {e}")

class PerformanceOptimizer:
    """Optimizes system performance based on 18-hour analysis"""

    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []
        self.optimization_strategies: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)

    def record_metric(self, name: str, value: float, timestamp: datetime = None):
        """Record a performance metric"""
        if timestamp is None:
            timestamp = datetime.now()

        self.metrics_history.append({
            "name": name,
            "value": value,
            "timestamp": timestamp,
            "hash": self._generate_metric_hash(name, value, timestamp)
        })

        # Keep only last 1000 metrics
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]

    def _generate_metric_hash(self, name: str, value: float, timestamp: datetime) -> str:
        """Generate hash for metric deduplication"""
        data = f"{name}{value}{timestamp.isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()

    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance metrics and provide insights"""
        if not self.metrics_history:
            return {"status": "no_data"}

        # Group metrics by name
        metrics_by_name = {}
        for metric in self.metrics_history:
            name = metric["name"]
            if name not in metrics_by_name:
                metrics_by_name[name] = []
            metrics_by_name[name].append(metric)

        analysis = {}
        for name, metrics in metrics_by_name.items():
            values = [m["value"] for m in metrics]
            analysis[name] = {
                "count": len(values),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "latest": values[-1],
                "trend": self._calculate_trend(values)
            }

        return analysis

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from values"""
        if len(values) < 2:
            return "stable"

        # Simple trend calculation
        recent_avg = sum(values[-5:]) / min(5, len(values))
        older_avg = sum(values[:-5]) / max(1, len(values) - 5)

        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"

    def register_optimization_strategy(self, name: str, strategy: Callable):
        """Register an optimization strategy"""
        self.optimization_strategies[name] = strategy
        self.logger.info(f"Registered optimization strategy: {name}")

    async def apply_optimizations(self) -> Dict[str, Any]:
        """Apply registered optimization strategies"""
        results = {}

        for name, strategy in self.optimization_strategies.items():
            try:
                result = await strategy() if asyncio.iscoroutinefunction(strategy) else strategy()
                results[name] = {"status": "success", "result": result}
                self.logger.info(f"Applied optimization strategy: {name}")
            except Exception as e:
                results[name] = {"status": "failed", "error": str(e)}
                self.logger.error(f"Optimization strategy {name} failed: {e}")

        return results

def resilient(circuit_breaker_config: CircuitBreakerConfig = None):
    """Decorator for making functions resilient"""
    def decorator(func):
        circuit_breaker = CircuitBreaker(circuit_breaker_config)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await circuit_breaker.execute(func, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(circuit_breaker.execute(func, *args, **kwargs))

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Global resilience manager instance
resilience_manager = {
    "dependency_manager": DependencyManager(),
    "interruption_preventer": InterruptionPreventer(),
    "performance_optimizer": PerformanceOptimizer()
}

# Example usage and initialization
def initialize_resilience():
    """Initialize resilience management"""
    dep_manager = resilience_manager["dependency_manager"]

    # Register common dependencies
    dep_manager.register_dependency(DependencyConfig(
        name="openai_api",
        timeout=30.0,
        retry_attempts=3,
        circuit_breaker_config=CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=60.0
        )
    ))

    dep_manager.register_dependency(DependencyConfig(
        name="vector_database",
        timeout=10.0,
        retry_attempts=2,
        circuit_breaker_config=CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=30.0
        )
    ))

    logging.info("Resilience manager initialized")

if __name__ == "__main__":
    # Example usage
    async def example_usage():
        initialize_resilience()

        # Example resilient function
        @resilient(CircuitBreakerConfig(failure_threshold=3))
        async def risky_operation():
            # Simulate potential failure
            import random
            if random.random() < 0.3:
                raise Exception("Random failure")
            return "Success"

        try:
            result = await risky_operation()
            print(f"Operation result: {result}")
        except Exception as e:
            print(f"Operation failed: {e}")

    asyncio.run(example_usage())
