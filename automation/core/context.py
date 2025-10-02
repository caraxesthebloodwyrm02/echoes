"""Context management for the automation framework."""

import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Context:
    """Execution context for automation tasks.

    Attributes:
        dry_run: If True, tasks should not make any changes
        user: Current user
        env: Current environment (e.g., 'dev', 'staging', 'prod')
        confirmed: Whether user has confirmed an action
        extra: Additional context data
    """

    dry_run: bool = False
    user: str = field(
        default_factory=lambda: os.getenv("USERNAME") or os.getenv("USER") or "unknown"
    )
    env: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "dev"))
    confirmed: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    def require_confirmation(self, message: str) -> bool:
        """Prompt the user for confirmation.

        Args:
            message: The message to display to the user

        Returns:
            bool: True if confirmed, False otherwise
        """
        if self.dry_run:
            return True

        response = input(f"{message} [y/N]: ").strip().lower()
        self.confirmed = response == "y"
        return self.confirmed
