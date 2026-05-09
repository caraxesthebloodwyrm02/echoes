#!/usr/bin/env python3
"""
Gridstral / Mistral Agents — beta conversation demo

Uses the official Mistral Python SDK (``mistralai``) with:

- ``beta.conversations.start`` + ``agent_id`` / optional ``agent_version``
- When **no** ``GRIDSTRAL_AGENT_ID``: optional ``completion_args`` with
  ``MISTRAL_MODEL`` (default ``mistral-medium-latest``).
- When **using an agent**: **do not** pass ``completion_args`` — the Mistral API
  rejects it (model/version live on the agent in La Plateforme).

**Never commit API keys.** Set ``MISTRAL_API_KEY`` in the environment.

Environment
-----------

======================= ===================================================
Variable                Meaning
======================= ===================================================
``MISTRAL_API_KEY``     Required for a live call.
``GRIDSTRAL_AGENT_ID``  Mistral Agent id (``ag_…``).
``GRIDSTRAL_AGENT_VERSION`` Optional pinned version (integer), e.g. ``32``.
``MISTRAL_MODEL``       Defaults to ``mistral-medium-latest``.
``GRIDSTRAL_INPUTS_JSON`` Optional path to a JSON file: either a **list** of
                        conversation items, or ``{"inputs": [...]}``.
======================= ===================================================

Install deps::

    uv sync --group mistral

Run::

    uv run python examples/gridstral_mistral_conversation_demo.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


def _default_inputs() -> list[dict[str, Any]]:
    """Minimal smoke transcript — replace with GRIDSTRAL_INPUTS_JSON for long runs."""
    return [
        {"role": "user", "content": "hello — classify my task as Chat / Analysis / Status / Planning."},
    ]


def _load_inputs() -> list[dict[str, Any]]:
    path = os.getenv("GRIDSTRAL_INPUTS_JSON")
    if not path:
        return _default_inputs()
    p = Path(path).expanduser()
    raw = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "inputs" in raw:
        return raw["inputs"]  # type: ignore[return-value]
    if isinstance(raw, list):
        return raw
    raise ValueError("GRIDSTRAL_INPUTS_JSON must be a JSON array or {\"inputs\": [...]}")


def main() -> None:
    key = os.getenv("MISTRAL_API_KEY")
    if not key:
        print(
            "Set MISTRAL_API_KEY in the environment (do not paste keys into git).\n"
            "Example: export MISTRAL_API_KEY='…'\n"
            "Install SDK: uv sync --group mistral",
            file=sys.stderr,
        )
        sys.exit(2)

    agent_id = os.getenv("GRIDSTRAL_AGENT_ID")
    if not agent_id:
        print(
            "Set GRIDSTRAL_AGENT_ID to your Mistral Agent id (ag_…).\n"
            "Create/configure the agent in Mistral La Plateforme with mistral-medium-latest.",
            file=sys.stderr,
        )
        sys.exit(2)

    inputs = _load_inputs()

    try:
        from mistralai.client import Mistral
    except ImportError:
        print("Install mistralai: uv sync --group mistral", file=sys.stderr)
        sys.exit(2)

    client = Mistral(api_key=key)

    kwargs: dict[str, Any] = {"inputs": inputs, "agent_id": agent_id}

    ver_raw = os.getenv("GRIDSTRAL_AGENT_VERSION")
    if ver_raw is not None and ver_raw.strip() != "":
        kwargs["agent_version"] = int(ver_raw)

    response = client.beta.conversations.start(**kwargs)

    if hasattr(response, "model_dump"):
        print(json.dumps(response.model_dump(mode="json"), indent=2, ensure_ascii=False))
    else:
        print(response)


if __name__ == "__main__":
    main()
