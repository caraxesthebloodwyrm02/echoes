"""CI/CD monitoring utilities."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from packages.core import get_logger

logger = get_logger("monitoring.ci")


@dataclass
class CIBuild:
    """CI build information."""

    build_id: str
    status: str
    branch: str
    commit: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]


class CIMonitor:
    """Monitors CI/CD pipelines."""

    def __init__(self) -> None:
        self.logger = logger
        self.builds: List[CIBuild] = []

    def add_build(self, build: CIBuild) -> None:
        """Add a build to monitoring."""
        self.builds.append(build)
        self.logger.info(f"Tracking build {build.build_id}: {build.status}")


__all__ = ["CIBuild", "CIMonitor"]
