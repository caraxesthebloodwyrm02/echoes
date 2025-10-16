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

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ExecutionContext(BaseModel):
    """Immutable execution metadata passed to every expert."""

    run_id: str
    dry_run: bool = False
    user_id: Optional[str] = None
    logger: Any
    config: Dict[str, Any]
    tags: Dict[str, Any] = {}


class BaseExpert(ABC):
    """Abstract base class for all MoE experts."""

    name: str = ""
    version: str = "0.1.0"
    request_schema: type[BaseModel] | None = None
    response_schema: type[BaseModel] | None = None

    @abstractmethod
    def can_handle(self, request: BaseModel) -> bool:
        """Return True if expert can process the given request payload."""

    @abstractmethod
    async def process(self, request: BaseModel, ctx: ExecutionContext) -> BaseModel:
        """Execute the expert logic and return a response model."""
