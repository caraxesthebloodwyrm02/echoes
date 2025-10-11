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
