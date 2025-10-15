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

import asyncio
import os
from functools import lru_cache
from typing import Any, Dict, List, Literal, Optional

from fastapi import Depends, FastAPI, HTTPException
from minicon.config import Config
from pydantic import BaseModel, Field

app = FastAPI(title="Symphony Assistance API", version="1.0.0")


@lru_cache
def get_config() -> Config:
    """Load configuration from environment once per process."""
    return Config.from_env()


def get_openai_client() -> Any:
    """Provide the active OpenAI client from the shared configuration."""
    return get_config().openai_client


class AssistRequest(BaseModel):
    prompt: str = Field(..., description="User prompt or question")
    model: Optional[str] = Field(None, description="Override model identifier")
    temperature: float = Field(0.2, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(512, gt=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AssistResponse(BaseModel):
    model: str
    content: str
    usage: Optional[Dict[str, Any]] = None


class SwitchKeyRequest(BaseModel):
    key_type: Literal["PRIMARY", "SECONDARY"]


class SwitchKeyResponse(BaseModel):
    status: str
    active_key: str


class ModelsResponse(BaseModel):
    models: List[str]


def _extract_response_text(response: Any) -> str:
    """Utility to flatten OpenAI Responses API payloads."""
    if not hasattr(response, "output"):
        return ""

    texts: List[str] = []
    for item in getattr(response, "output", []):
        for content in getattr(item, "content", []):
            text = getattr(content, "text", None)
            if text:
                texts.append(text)
    return "\n".join(texts).strip()


@app.post("/assistant/query", response_model=AssistResponse)
async def assistant_query(
    request: AssistRequest,
    client: Any = Depends(get_openai_client),
) -> AssistResponse:
    """Submit a prompt to OpenAI and return the generated content."""
    model = request.model or os.getenv("LLM_MODEL_PRIMARY", "gpt-4o-mini")
    kwargs: Dict[str, Any] = {
        "model": model,
        "input": request.prompt,
        "temperature": request.temperature,
    }
    if request.max_tokens is not None:
        kwargs["max_output_tokens"] = request.max_tokens
    if request.metadata:
        kwargs["metadata"] = request.metadata

    loop = asyncio.get_event_loop()
    try:
        response = await loop.run_in_executor(
            None, lambda: client.responses.create(**kwargs)
        )
    except Exception as exc:  # pragma: no cover - actual API errors
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    content = _extract_response_text(response)
    return AssistResponse(
        model=getattr(response, "model", model),
        content=content,
        usage=getattr(response, "usage", None),
    )


@app.post("/assistant/switch-key", response_model=SwitchKeyResponse)
async def switch_api_key(request: SwitchKeyRequest) -> SwitchKeyResponse:
    """Switch between PRIMARY and SECONDARY API keys."""
    config = get_config()
    try:
        config.switch_api_key(request.key_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return SwitchKeyResponse(status="ok", active_key=config.active_openai_key)


@app.get("/assistant/models", response_model=ModelsResponse)
async def list_models(client: Any = Depends(get_openai_client)) -> ModelsResponse:
    """List available models for the active API key."""
    loop = asyncio.get_event_loop()
    try:
        models = await loop.run_in_executor(None, lambda: client.models.list())
    except Exception as exc:  # pragma: no cover - actual API errors
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    model_ids = [getattr(model, "id", "") for model in getattr(models, "data", [])]
    return ModelsResponse(models=model_ids)
