"""Tests for EchoesAgentsV1 runtime spec and Pydantic envelope (no live OpenAI)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.echoes_agents_v1 import (
    EchoesAgentV1Envelope,
    EchoesAssistantRuntimeSpec,
    envelope_json_schema,
    model_to_runtime_spec,
    runtime_spec_to_model,
    snapshot_runtime_spec,
)


@pytest.fixture
def sample_spec() -> EchoesAssistantRuntimeSpec:
    return EchoesAssistantRuntimeSpec(
        enable_rag=True,
        enable_tools=False,
        enable_streaming=True,
        enable_status=False,
        enable_glimpse=True,
        enable_external_contact=False,
        enable_value_system=True,
        enable_knowledge_graph=False,
        enable_multimodal_resonance=True,
        enable_legal_safeguards=False,
        session_id="sess_test",
        model="gpt-4o-mini",
        temperature=0.2,
        max_tokens=900,
    )


def test_snapshot_runtime_spec_from_simple_namespace() -> None:
    assistant = SimpleNamespace(
        enable_rag=1,  # truthy
        enable_tools=0,
        enable_streaming=True,
        enable_status=False,
        enable_glimpse=True,
        enable_external_contact=False,
        enable_value_system=True,
        enable_knowledge_graph=True,
        enable_multimodal_resonance=False,
        enable_legal_safeguards=True,
        session_id="abc",
        model=None,
        temperature=0.7,
        max_tokens=None,
    )
    spec = snapshot_runtime_spec(assistant)
    assert spec.enable_rag is True
    assert spec.enable_tools is False
    assert spec.session_id == "abc"
    assert spec.model is None


def test_roundtrip_pydantic(sample_spec: EchoesAssistantRuntimeSpec) -> None:
    model = runtime_spec_to_model(sample_spec)
    back = model_to_runtime_spec(model)
    assert back == sample_spec


def test_envelope_roundtrip_json(sample_spec: EchoesAssistantRuntimeSpec) -> None:
    env = EchoesAgentV1Envelope(runtime=runtime_spec_to_model(sample_spec))
    data = env.model_dump(mode="json")
    env2 = EchoesAgentV1Envelope.model_validate(data)
    assert model_to_runtime_spec(env2.runtime) == sample_spec


def test_envelope_json_schema_has_root_keys() -> None:
    schema = envelope_json_schema()
    assert schema.get("title") == "EchoesAgentV1Envelope" or "EchoesAgentV1Envelope" in str(
        schema.get("$defs", {})
    )
    assert "runtime" in schema.get("properties", {})


def test_forbid_extra_envelope() -> None:
    with pytest.raises(ValidationError):
        EchoesAgentV1Envelope.model_validate(
            {
                "schema_id": "echoes-agents-v1",
                "runtime": {
                    "enable_rag": True,
                    "enable_tools": True,
                    "enable_streaming": True,
                    "enable_status": True,
                    "enable_glimpse": True,
                    "enable_external_contact": True,
                    "enable_value_system": True,
                    "enable_knowledge_graph": True,
                    "enable_multimodal_resonance": True,
                    "enable_legal_safeguards": True,
                },
                "unknown": 1,
            }
        )
