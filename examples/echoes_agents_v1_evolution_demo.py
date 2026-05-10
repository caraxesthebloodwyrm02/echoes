#!/usr/bin/env python3
"""
EchoesAgentsV1 evolution: legacy chat-style assistant → GPT-5.5 / Codex-style agent.

This script uses the *inventory* in ``app/echoes_agents_v1``:

- :class:`EchoesAssistantRuntimeSpec` — frozen dataclass of effective toggles and
  model overrides (all ``bool`` flags + ``session_id``, ``model``, ``temperature``,
  ``max_tokens``).
- :func:`snapshot_runtime_spec` — duck-typed reader for any object with those attrs
  (e.g. :class:`EchoesAssistantV2`).
- :class:`EchoesAgentV1Envelope` / :class:`EchoesAssistantRuntimeSpecModel` —
  Pydantic v2 envelope ``schema_id == "echoes-agents-v1"``, strict extras forbidden.

Arithmetic metaphor (precision of “what is an agent?”):

  **minuend**    − **subtrahend** = **difference**

  - **Minuend**: the capability envelope we attribute to a **GPT-5.5-era Codex-oriented
    agent** — tools, retrieval, guardrails, multimodal hooks, API coupling (maximum
    intentional surface).
  - **Subtrahend**: the **baseline “assistant”** — conversational completion with
    minimal agentic affordances (classic GPT-4-style *chat* posture).
  - **Difference (remainder)**: the Boolean/feature delta that names what “agent”
    means here — not the union of everything, but the **set subtract** that remains
    once you remove the baseline assistant fiction.

Community framing (2026): GPT-5.5 is positioned as a frontier model for professional
and coding/agentic workflows; **Codex** (CLI / IDE agent) is the recommended shell for
code-heavy tool loops — pair ``gpt-5.5`` with Codex where your workflow is repo edits,
tests, and CI. API availability evolves; this demo stays runnable without a key.

**GridStral profile (Mistral API):** Set ``MISTRAL_API_KEY`` or ``GRIDSTRAL_API_KEY``.
The demo uses Mistral's OpenAI-compatible endpoint (``https://api.mistral.ai/v1``) with
defaults ``mistral-small-latest`` (subtrahend) and ``mistral-medium-latest`` (minuend).

Run::

    uv run python examples/echoes_agents_v1_evolution_demo.py

Environment::

    MISTRAL_API_KEY / GRIDSTRAL_API_KEY — optional; preferred when set (GridStral demo).
    OPENAI_API_KEY   — optional; used when no Mistral key is set.
    EVOLUTION_MODEL_LEGACY — overrides legacy profile model (defaults depend on backend).
    EVOLUTION_MODEL_AGENT  — overrides agent profile model (defaults depend on backend).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.echoes_agents_v1 import (  # noqa: E402
    EchoesAgentV1Envelope,
    EchoesAssistantRuntimeSpec,
    runtime_spec_to_model,
)

MISTRAL_BASE_URL = "https://api.mistral.ai/v1"


def _mistral_key() -> str | None:
    return os.getenv("MISTRAL_API_KEY") or os.getenv("GRIDSTRAL_API_KEY")


def _using_mistral() -> bool:
    return bool(_mistral_key())


def default_legacy_model() -> str:
    if _using_mistral():
        return os.getenv("EVOLUTION_MODEL_LEGACY", "mistral-small-latest")
    return os.getenv("EVOLUTION_MODEL_LEGACY", "gpt-4o")


def default_agent_model() -> str:
    if _using_mistral():
        return os.getenv("EVOLUTION_MODEL_AGENT", "mistral-medium-latest")
    return os.getenv("EVOLUTION_MODEL_AGENT", "gpt-5.5")


def legacy_gpt4_style_assistant_spec(session_id: str) -> EchoesAssistantRuntimeSpec:
    """Subtrahend: chat-first posture — minimal agentic surface."""
    return EchoesAssistantRuntimeSpec(
        enable_rag=False,
        enable_tools=False,
        enable_streaming=True,
        enable_status=False,
        enable_glimpse=False,
        enable_external_contact=False,
        enable_value_system=False,
        enable_knowledge_graph=False,
        enable_multimodal_resonance=False,
        enable_legal_safeguards=False,
        session_id=session_id,
        model=default_legacy_model(),
        temperature=0.7,
        max_tokens=1024,
    )


def gpt55_codex_agent_style_spec(session_id: str) -> EchoesAssistantRuntimeSpec:
    """Minuend: Codex-oriented agent — tools, retrieval, guardrails, coupling."""
    return EchoesAssistantRuntimeSpec(
        enable_rag=True,
        enable_tools=True,
        enable_streaming=True,
        enable_status=True,
        enable_glimpse=True,
        enable_external_contact=True,
        enable_value_system=True,
        enable_knowledge_graph=True,
        enable_multimodal_resonance=True,
        enable_legal_safeguards=True,
        session_id=session_id,
        model=default_agent_model(),
        temperature=0.3,
        max_tokens=8192,
    )


def spec_boolean_delta(minuend: EchoesAssistantRuntimeSpec, subtrahend: EchoesAssistantRuntimeSpec) -> dict[str, bool]:
    """
    Per-flag XOR on boolean fields only — highlights where profiles diverge.

    For narrative clarity we also emit ``agent_surplus``: flags True in minuend but
    not in subtrahend (the usual “what did we add for agent?” story).
    """
    keys = (
        "enable_rag",
        "enable_tools",
        "enable_streaming",
        "enable_status",
        "enable_glimpse",
        "enable_external_contact",
        "enable_value_system",
        "enable_knowledge_graph",
        "enable_multimodal_resonance",
        "enable_legal_safeguards",
    )
    surplus: dict[str, bool] = {}
    xor: dict[str, bool] = {}
    for k in keys:
        a = getattr(minuend, k)
        b = getattr(subtrahend, k)
        xor[k] = bool(a) ^ bool(b)
        surplus[k] = bool(a) and not bool(b)
    return {"xor": xor, "agent_surplus": surplus}


def envelope_dump(spec: EchoesAssistantRuntimeSpec) -> dict:
    env = EchoesAgentV1Envelope(runtime=runtime_spec_to_model(spec))
    return env.model_dump(mode="json")


def optional_openai_narration(agent_surplus: dict[str, bool]) -> None:
    """One completion contrasting baseline vs agent if OPENAI_API_KEY is set."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("\n[skip] OPENAI_API_KEY not set — no live model call.")
        print("       Export OPENAI_API_KEY to narrate the remainder via the API.")
        return

    try:
        from openai import OpenAI
    except ImportError:
        print("\n[skip] openai package not importable.")
        return

    client = OpenAI(api_key=key)
    enabled = [k for k, v in agent_surplus.items() if v]
    prompt = (
        "In under 120 words, explain why the following capability flags (enabled on "
        "the agent profile but off on a minimal chat assistant) operationalize the "
        "idea of a software agent vs a plain assistant: "
        + ", ".join(enabled)
        + ". Mention GPT-5.5-level reasoning density and Codex-style tool loops "
        "without claiming proprietary details."
    )
    model = os.getenv("EVOLUTION_MODEL_AGENT", "gpt-5.5")
    fallback = os.getenv("EVOLUTION_MODEL_LEGACY", "gpt-4o")
    for attempt_model in (model, fallback):
        try:
            res = client.chat.completions.create(
                model=attempt_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
            )
            text = (res.choices[0].message.content or "").strip()
            print(f"\n--- Model narration ({attempt_model}) ---\n{text}\n")
            return
        except Exception as e:
            if attempt_model == fallback:
                print(f"\n[skip] Narration failed after {model} and {fallback}: {e!s}")
                print("       Check quota/billing or unset OPENAI_API_KEY for envelope-only mode.")
            else:
                print(f"\n[warn] {attempt_model} failed ({e!s}); retrying with {fallback}.")


def main() -> None:
    sid = "evolution_demo_session"
    sub = legacy_gpt4_style_assistant_spec(sid)
    minuend = gpt55_codex_agent_style_spec(sid)

    delta = spec_boolean_delta(minuend, sub)

    print("EchoesAgentsV1 — minuend / subtrahend / difference")
    print("=" * 72)
    print("\n[Subtrahend envelope — legacy chat-style assistant]")
    print(json.dumps(envelope_dump(sub), indent=2))
    print("\n[Minuend envelope — GPT-5.5 / Codex-oriented agent profile]")
    print(json.dumps(envelope_dump(minuend), indent=2))
    print("\n[Difference — XOR per flag]")
    print(json.dumps(delta["xor"], indent=2))
    print("\n[Agent surplus — True on agent, False on baseline]")
    print(json.dumps(delta["agent_surplus"], indent=2))

    optional_openai_narration(delta["agent_surplus"])

    html_path = Path(__file__).with_name("echoes_agents_v1_evolution_canvas.html")
    if html_path.is_file():
        print(f"\n[visual] Open in browser: file://{html_path}")
        print("         Or serve: uv run python -m http.server 8765 --directory examples")
        print("         then http://localhost:8765/echoes_agents_v1_evolution_canvas.html")


if __name__ == "__main__":
    main()
