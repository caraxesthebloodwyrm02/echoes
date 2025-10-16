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
