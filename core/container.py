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

# MIT License
# Copyright (c) 2025 Echoes Project

"""
Dependency Injection Container
Lightweight service container with provider pattern
"""

import inspect
import logging
from typing import Any, Callable, Dict, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceContainer:
    """
    Lightweight dependency injection container

    Features:
    - Service registration (singleton, transient, scoped)
    - Factory functions
    - Automatic dependency resolution
    - Lifecycle management
    """

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._transients: Dict[str, Type] = {}
        self.logger = logging.getLogger(__name__)

    def register_singleton(self, name: str, instance: Any):
        """Register a singleton instance"""
        self._singletons[name] = instance
        self.logger.debug(f"Registered singleton: {name}")

    def register_transient(self, name: str, cls: Type[T]):
        """Register a transient service (new instance each time)"""
        self._transients[name] = cls
        self.logger.debug(f"Registered transient: {name}")

    def register_factory(self, name: str, factory: Callable[..., Any]):
        """Register a factory function"""
        self._factories[name] = factory
        self.logger.debug(f"Registered factory: {name}")

    def resolve(self, name: str) -> Any:
        """
        Resolve a service by name

        Resolution order:
        1. Singletons
        2. Factories
        3. Transients (creates new instance)
        """
        # Check singletons first
        if name in self._singletons:
            return self._singletons[name]

        # Check factories
        if name in self._factories:
            factory = self._factories[name]
            # Resolve factory dependencies
            return self._invoke_with_dependencies(factory)

        # Check transients
        if name in self._transients:
            cls = self._transients[name]
            return self._create_instance(cls)

        raise ValueError(f"Service '{name}' not registered")

    def _create_instance(self, cls: Type[T]) -> T:
        """Create instance with automatic dependency resolution"""
        try:
            # Get constructor signature
            sig = inspect.signature(cls.__init__)
            params = sig.parameters

            # Skip 'self' parameter
            kwargs = {}
            for param_name, param in params.items():
                if param_name == "self":
                    continue

                # Try to resolve dependency
                try:
                    kwargs[param_name] = self.resolve(param_name)
                except ValueError:
                    # Use default if available
                    if param.default != inspect.Parameter.empty:
                        kwargs[param_name] = param.default

            return cls(**kwargs)

        except Exception as e:
            self.logger.error(f"Failed to create instance of {cls.__name__}: {e}")
            # Try without dependencies
            return cls()

    def _invoke_with_dependencies(self, func: Callable) -> Any:
        """Invoke function with automatic dependency resolution"""
        try:
            sig = inspect.signature(func)
            kwargs = {}

            for param_name, param in sig.parameters.items():
                try:
                    kwargs[param_name] = self.resolve(param_name)
                except ValueError:
                    if param.default != inspect.Parameter.empty:
                        kwargs[param_name] = param.default

            return func(**kwargs)

        except Exception as e:
            self.logger.error(f"Failed to invoke {func.__name__}: {e}")
            return func()

    def has(self, name: str) -> bool:
        """Check if service is registered"""
        return (
            name in self._singletons
            or name in self._factories
            or name in self._transients
        )

    def clear(self):
        """Clear all registered services"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._transients.clear()
        self.logger.info("Service container cleared")


class ServiceProvider:
    """
    Service provider base class
    Implement this to create custom service providers
    """

    def __init__(self, container: ServiceContainer):
        self.container = container

    def register_services(self):
        """Override to register services"""
        raise NotImplementedError


class Context:
    """
    Execution context for request/operation scope
    """

    def __init__(self, container: ServiceContainer):
        self.container = container
        self._local_services: Dict[str, Any] = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._local_services.clear()

    def get_service(self, name: str) -> Any:
        """Get service (scoped or from container)"""
        if name in self._local_services:
            return self._local_services[name]
        return self.container.resolve(name)

    def set_local_service(self, name: str, instance: Any):
        """Set service in local scope"""
        self._local_services[name] = instance


__all__ = ["ServiceContainer", "ServiceProvider", "Context"]
