"""Task generation and management."""

from dataclasses import dataclass
from typing import Any


@dataclass
class TaskDefinition:
    """Structured task definition."""

    task_id: str
    task_name: str
    severity: str  # low|medium|high
    category: str  # lint|refactor|security|testing
    files: list[str]
    lines: list[int] | None = None
    description: str = ""
    suggested_fix: str = ""
    automated: bool = True
    status: str = "pending"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "severity": self.severity,
            "category": self.category,
            "files": self.files,
            "lines": self.lines,
            "description": self.description,
            "suggested_fix": self.suggested_fix,
            "automated": self.automated,
            "status": self.status,
        }

    def determine_severity(self, pattern_name: str) -> str:
        """Determine task severity based on pattern.

        Args:
            pattern_name: Name of the pattern

        Returns:
            Severity level: low|medium|high
        """
        # High severity patterns
        high_patterns = {
            "password",
            "token",
            "secret",
            "key",
            "bare_except",
            "broad_except",
        }
        # Medium severity patterns
        medium_patterns = {"mutable_default", "unused_import", "todo", "fixme"}
        # Low severity patterns
        low_patterns = {"technical_debt", "temporary"}  # Updated from "hack"

        if pattern_name in high_patterns:
            return "high"
        elif pattern_name in medium_patterns:
            return "medium"
        else:
            return "low"

    def determine_category(self, pattern_name: str) -> str:
        """Determine task category based on pattern.

        Args:
            pattern_name: Name of the pattern

        Returns:
            Category: lint|refactor|security|testing
        """
        security_patterns = {"password", "token", "secret", "key"}
        testing_patterns = {"todo", "fixme"}
        lint_patterns = {"unused_import", "mutable_default"}
        refactor_patterns = {
            "technical_debt",
            "temporary",
            "bare_except",
            "broad_except",
        }  # Updated from "hack"

        if pattern_name in security_patterns:
            return "security"
        elif pattern_name in testing_patterns:
            return "testing"
        elif pattern_name in lint_patterns:
            return "lint"
        elif pattern_name in refactor_patterns:
            return "refactor"
        else:
            return "lint"  # Default

    def generate_task_id(self, pattern_name: str, file_path: str) -> str:
        """Generate a unique task ID.

        Args:
            pattern_name: Name of the pattern
            file_path: Path to the file containing the pattern

        Returns:
            A unique task ID string
        """
        import hashlib
        import os

        # Create a unique hash based on pattern and file path
        content = f"{pattern_name}:{file_path}"
        hash_object = hashlib.md5(content.encode())
        hash_value = hash_object.hexdigest()[:3]

        # Get a numerical identifier
        basename = os.path.splitext(os.path.basename(file_path))[0]
        return f"{pattern_name}_{hash_value}"

    def generate_task_description(self, pattern_name: str) -> tuple[str, str]:
        """Generate task description and suggested fix.

        Args:
            pattern_name: Name of the pattern

        Returns:
            Tuple of (description, suggested_fix)
        """
        # Generate descriptions and fixes based on pattern
        descriptions = {
            "todo": "Remove or implement TODO comments",
            "fixme": "Address FIXME comments in the code",
            "technical_debt": "Review and improve technical debt items",
            "interim_solution": "Convert interim solutions to permanent implementations",  # Updated from "temporary"
            "unused_import": "Remove unused import statements",
            "bare_except": "Replace bare except clauses with specific exception handling",
            "broad_except": "Replace broad exception handling with specific exceptions",
            "mutable_default": "Fix mutable default arguments in function definitions",
            "password": "Review and secure password/secret handling",
        }

        fixes = {
            "todo": "Implement the TODO item or remove if no longer needed",
            "fixme": "Fix the identified issue and remove the FIXME comment",
            "technical_debt": "Refactor the code following best practices and design patterns",
            "interim_solution": "Replace interim/temporary solutions with proper, production-ready implementations",  # Enhanced fix description
            "unused_import": "Remove unused import statements",
            "bare_except": "Specify the exact exception type being caught",
            "broad_except": "Handle specific exceptions instead of catching all",
            "mutable_default": "Use None as default and initialize mutable object inside function",
            "password": "Move secrets to environment variables or secure storage",
        }

        return (
            descriptions.get(pattern_name, f"Fix {pattern_name} issues"),
            fixes.get(
                pattern_name, f"Address {pattern_name} according to best practices"
            ),
        )
