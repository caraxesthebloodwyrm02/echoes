import json
import logging
import os
import re
from typing import Any, Dict, Optional

import requests

log = logging.getLogger(__name__)


# -------------------------
# Provider implementations
# -------------------------
def _openai_chat(prompt: str, model: str = "gpt-4o-mini") -> str:
    """OpenAI Chat Completions (v1 client)."""
    try:
        from openai import OpenAI  # type: ignore
    except ImportError as exc:
        raise RuntimeError("openai package not installed") from exc

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment")

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
    )
    return (resp.choices[0].message.content or "").strip()


def _ollama_chat(prompt: str, model: str = "llama3.1:8b") -> str:
    """Call a local Ollama server."""
    url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api/generate")
    headers = {}
    token = os.getenv("OLLAMA_API_KEY")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    payload = {"model": model, "prompt": prompt, "stream": False}
    r = requests.post(url, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()
    # Ollama returns plain text in "response"
    return str(data.get("response", "")).strip()


def _gemini_chat(prompt: str, model: str = "gemini-1.5-flash") -> str:
    """Minimal REST call to Gemini (Generative Language API)."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set in environment")
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(endpoint, json=body, timeout=60)
    r.raise_for_status()
    data = r.json()
    # Extract first text candidate
    try:
        return data["candidates"][0]["content"]["parts"][0][
            "text"
        ].strip()  # type: ignore[index]
    except Exception:
        log.warning("Unexpected Gemini response: %s", str(data)[:200])
        return ""


class LLMClient:
    def __init__(self):
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.provider = provider
        # Default models per provider
        if provider == "openai":
            self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        elif provider == "ollama":
            self.model = os.getenv("LLM_MODEL", "llama3.1:8b")
        elif provider == "gemini":
            self.model = os.getenv("LLM_MODEL", "gemini-1.5-flash")
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER={provider}")

    def complete(self, prompt: str) -> str:
        if self.provider == "openai":
            return _openai_chat(prompt, model=self.model)
        if self.provider == "ollama":
            return _ollama_chat(prompt, model=self.model)
        if self.provider == "gemini":
            return _gemini_chat(prompt, model=self.model)
        raise RuntimeError("No LLM backend configured")

    @staticmethod
    def parse_json_response(text: str) -> Optional[Dict[str, Any]]:
        cleaned = text.strip()

        # Handle Markdown code fences like ```json ... ```
        if cleaned.startswith("```"):
            match = re.match(
                r"```(?:json)?\s*(.*?)\s*```$", cleaned, re.DOTALL | re.IGNORECASE
            )
            if match:
                cleaned = match.group(1).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            log.warning("LLM returned non-JSON: %s", text[:200])
            return None
