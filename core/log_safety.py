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
Safe Exception Handler

Standardizes exception handling across the codebase.
Provides logging, recovery, and monitoring capabilities.
"""

import functools
import json
import logging
import traceback
from typing import Any, Callable, Dict, List, Optional, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class SafeExecutionError(Exception):
    """Custom exception for safe execution failures."""

    pass


class ExecutionContext:
    """Context information for exception handling."""

    def __init__(
        self,
        function_name: str,
        module: str = "",
        args: tuple = (),
        kwargs: dict = None,
    ):
        self.function_name = function_name
        self.module = module
        self.args = args
        self.kwargs = kwargs or {}
        self.timestamp = None
        self.execution_id = None

    def __str__(self):
        return f"{self.module}.{self.function_name}({self.args}, {self.kwargs})"


class ErrorHandler:
    """Centralized error handling and recovery."""

    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self.error_log: List[Dict[str, Any]] = []

        # Default recovery strategies
        self._setup_default_strategies()

    def _setup_default_strategies(self):
        """Set up default error recovery strategies."""
        self.recovery_strategies = {
            "FileNotFoundError": self._recover_file_not_found,
            "ConnectionError": self._recover_connection_error,
            "ValidationError": self._recover_validation_error,
            "KeyError": self._recover_key_error,
        }

    def _recover_file_not_found(self, error: Exception, context: ExecutionContext) -> Any:
        """Recover from file not found errors."""
        logger.warning(f"File not found in {context.function_name}: {error}")
        return None

    def _recover_connection_error(self, error: Exception, context: ExecutionContext) -> Any:
        """Recover from connection errors."""
        logger.warning(f"Connection error in {context.function_name}: {error}")
        return None

    def _recover_validation_error(self, error: Exception, context: ExecutionContext) -> Any:
        """Recover from validation errors."""
        logger.warning(f"Validation error in {context.function_name}: {error}")
        return None

    def _recover_key_error(self, error: Exception, context: ExecutionContext) -> Any:
        """Recover from key errors."""
        logger.warning(f"Key error in {context.function_name}: {error}")
        return None

    def handle_error(self, error: Exception, context: ExecutionContext, reraise: bool = True) -> Any:
        """Handle an error with optional recovery."""
        # Log the error
        self._log_error(error, context)

        # Try recovery strategy
        recovery_result = self._attempt_recovery(error, context)

        if recovery_result is not None:
            logger.info(f"Recovered from error in {context.function_name}")
            return recovery_result

        # No recovery available
        if reraise:
            raise SafeExecutionError(f"Unhandled error in {context.function_name}: {error}") from error

        logger.error(f"Unhandled error in {context.function_name}: {error}")
        return None

    def _log_error(self, error: Exception, context: ExecutionContext):
        """Log error details."""
        error_entry = {
            "function": context.function_name,
            "module": context.module,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "args": str(context.args),
            "kwargs": str(context.kwargs),
        }

        self.error_log.append(error_entry)

        # Update error counts
        error_key = f"{context.module}.{context.function_name}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

        # Log with appropriate level
        if isinstance(error, (FileNotFoundError, KeyError)):
            logger.warning(f"Error in {context.function_name}: {error}")
        else:
            logger.error(f"Error in {context.function_name}: {error}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")

    def _attempt_recovery(self, error: Exception, context: ExecutionContext) -> Any:
        """Attempt error recovery using registered strategies."""
        error_type = type(error).__name__

        if error_type in self.recovery_strategies:
            try:
                return self.recovery_strategies[error_type](error, context)
            except Exception as recovery_error:
                logger.error(f"Recovery strategy failed for {error_type}: {recovery_error}")

        return None

    def add_recovery_strategy(self, error_type: str, strategy: Callable):
        """Add a custom recovery strategy."""
        self.recovery_strategies[error_type] = strategy

    def get_error_stats(self) -> Dict[str, int]:
        """Get error statistics."""
        return self.error_counts.copy()

    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent error entries."""
        return self.error_log[-limit:] if self.error_log else []


# Global error handler instance
_error_handler = ErrorHandler()


def safe_exec(
    error_context: Optional[str] = None,
    reraise: bool = True,
    recovery_enabled: bool = True,
):
    """Decorator for safe function execution.

    Args:
        error_context: Optional context description for logging
        reraise: Whether to re-raise exceptions after handling
        recovery_enabled: Whether to attempt error recovery
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            context = ExecutionContext(
                function_name=func.__name__,
                module=func.__module__ or "",
                args=args,
                kwargs=kwargs,
            )

            try:
                return func(*args, **kwargs)
            except Exception as e:
                if recovery_enabled:
                    return _error_handler.handle_error(e, context, reraise)
                else:
                    # Log but don't attempt recovery
                    logger.error(f"Error in {func.__name__}: {e}")
                    if reraise:
                        raise

        return wrapper

    return decorator


def safe_call(func: Callable, *args, context: Optional[str] = None, reraise: bool = True, **kwargs) -> Any:
    """Safely call a function with error handling.

    Args:
        func: Function to call
        *args: Positional arguments
        context: Optional context description
        reraise: Whether to re-raise exceptions
        **kwargs: Keyword arguments

    Returns:
        Function result or None if error occurred
    """
    exec_context = ExecutionContext(
        function_name=getattr(func, "__name__", str(func)),
        module=getattr(func, "__module__", ""),
        args=args,
        kwargs=kwargs,
    )

    try:
        return func(*args, **kwargs)
    except Exception as e:
        if context:
            exec_context = ExecutionContext(
                function_name=f"{context}.{exec_context.function_name}",
                module=exec_context.module,
                args=args,
                kwargs=kwargs,
            )

        return _error_handler.handle_error(e, exec_context, reraise)


def with_error_context(context: str):
    """Decorator to add context to error messages."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                enhanced_message = f"{context}: {e}"
                raise type(e)(enhanced_message) from e

        return wrapper

    return decorator


# Convenience functions for common patterns
@safe_exec("file_operation")
def safe_read_file(file_path: str, default_content: str = "") -> str:
    """Safely read a file with error handling."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}")
        return default_content
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return default_content


@safe_exec("json_operation")
def safe_load_json(file_path: str, default_data: Any = None) -> Any:
    """Safely load JSON with error handling."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"JSON file not found: {file_path}")
        return default_data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return default_data
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {e}")
        return default_data


@safe_exec("api_operation")
def safe_api_call(api_func: Callable, *args, **kwargs) -> Any:
    """Safely call API functions with error handling."""
    return api_func(*args, **kwargs)


# Initialize error handler for the module
def get_error_stats() -> Dict[str, int]:
    """Get current error statistics."""
    return _error_handler.get_error_stats()


def get_recent_errors(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent error entries."""
    return _error_handler.get_recent_errors(limit)
