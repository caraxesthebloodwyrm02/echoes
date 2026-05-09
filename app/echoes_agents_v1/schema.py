"""Pydantic v2 schemas for EchoesAgentsV1 interchange and OpenAPI-friendly JSON Schema."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.echoes_agents_v1.runtime_spec import EchoesAssistantRuntimeSpec


class EchoesAssistantRuntimeSpecModel(BaseModel):
    """JSON-serializable mirror of :class:`EchoesAssistantRuntimeSpec`."""

    model_config = ConfigDict(extra="forbid")

    enable_rag: bool = Field(description="Whether retrieval augmentation is enabled.")
    enable_tools: bool = Field(description="Whether the tool registry is active.")
    enable_streaming: bool
    enable_status: bool
    enable_glimpse: bool
    enable_external_contact: bool
    enable_value_system: bool
    enable_knowledge_graph: bool
    enable_multimodal_resonance: bool
    enable_legal_safeguards: bool
    session_id: str | None = None
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None


class EchoesAgentV1Envelope(BaseModel):
    """
    Versioned document for agent runtime snapshots (config export, audits, future API).

    Not a database row — file or message payload only.
    """

    model_config = ConfigDict(extra="forbid")

    schema_id: Literal["echoes-agents-v1"] = "echoes-agents-v1"
    runtime: EchoesAssistantRuntimeSpecModel


def runtime_spec_to_model(spec: EchoesAssistantRuntimeSpec) -> EchoesAssistantRuntimeSpecModel:
    return EchoesAssistantRuntimeSpecModel(
        enable_rag=spec.enable_rag,
        enable_tools=spec.enable_tools,
        enable_streaming=spec.enable_streaming,
        enable_status=spec.enable_status,
        enable_glimpse=spec.enable_glimpse,
        enable_external_contact=spec.enable_external_contact,
        enable_value_system=spec.enable_value_system,
        enable_knowledge_graph=spec.enable_knowledge_graph,
        enable_multimodal_resonance=spec.enable_multimodal_resonance,
        enable_legal_safeguards=spec.enable_legal_safeguards,
        session_id=spec.session_id,
        model=spec.model,
        temperature=spec.temperature,
        max_tokens=spec.max_tokens,
    )


def model_to_runtime_spec(m: EchoesAssistantRuntimeSpecModel) -> EchoesAssistantRuntimeSpec:
    return EchoesAssistantRuntimeSpec(
        enable_rag=m.enable_rag,
        enable_tools=m.enable_tools,
        enable_streaming=m.enable_streaming,
        enable_status=m.enable_status,
        enable_glimpse=m.enable_glimpse,
        enable_external_contact=m.enable_external_contact,
        enable_value_system=m.enable_value_system,
        enable_knowledge_graph=m.enable_knowledge_graph,
        enable_multimodal_resonance=m.enable_multimodal_resonance,
        enable_legal_safeguards=m.enable_legal_safeguards,
        session_id=m.session_id,
        model=m.model,
        temperature=m.temperature,
        max_tokens=m.max_tokens,
    )


def envelope_json_schema() -> dict[str, Any]:
    """JSON Schema for :class:`EchoesAgentV1Envelope` (OpenAPI / tooling)."""
    return EchoesAgentV1Envelope.model_json_schema()
