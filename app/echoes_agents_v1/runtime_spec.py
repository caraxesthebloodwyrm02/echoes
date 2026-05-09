"""
Frozen runtime specification for EchoesAssistantV2–aligned agents.

EchoesAssistantV2 is a composite class (mixins), not a dataclass. This module
captures **effective** constructor-adjacent toggles for tooling, telemetry,
and JSON interchange without implying an ORM layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class EchoesAssistantRuntimeSpec:
    """Effective runtime flags and session/model overrides after assistant init."""

    enable_rag: bool
    enable_tools: bool
    enable_streaming: bool
    enable_status: bool
    enable_glimpse: bool
    enable_external_contact: bool
    enable_value_system: bool
    enable_knowledge_graph: bool
    enable_multimodal_resonance: bool
    enable_legal_safeguards: bool
    session_id: str | None
    model: str | None
    temperature: float | None
    max_tokens: int | None


def snapshot_runtime_spec(assistant: Any) -> EchoesAssistantRuntimeSpec:
    """
    Read effective toggles from an EchoesAssistantV2-like object (duck-typed).

    Missing attributes default to False / None so tests can pass lightweight mocks.
    """

    def _b(name: str, default: bool = False) -> bool:
        v = getattr(assistant, name, default)
        return bool(v) if v is not None else default

    def _o(name: str) -> Any:
        return getattr(assistant, name, None)

    return EchoesAssistantRuntimeSpec(
        enable_rag=_b("enable_rag"),
        enable_tools=_b("enable_tools"),
        enable_streaming=_b("enable_streaming"),
        enable_status=_b("enable_status"),
        enable_glimpse=_b("enable_glimpse"),
        enable_external_contact=_b("enable_external_contact"),
        enable_value_system=_b("enable_value_system"),
        enable_knowledge_graph=_b("enable_knowledge_graph"),
        enable_multimodal_resonance=_b("enable_multimodal_resonance"),
        enable_legal_safeguards=_b("enable_legal_safeguards"),
        session_id=_o("session_id"),
        model=_o("model"),
        temperature=_o("temperature"),
        max_tokens=_o("max_tokens"),
    )
