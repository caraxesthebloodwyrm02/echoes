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

import logging
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import privacy middleware
try:
    from packages.security.privacy_middleware import PrivacyMiddleware

    privacy_middleware = PrivacyMiddleware(filter_mode="mask")
except ImportError:
    # Fallback if privacy middleware not available
    privacy_middleware = None

app = FastAPI()

logger = logging.getLogger("service")
logger.setLevel(logging.INFO)


class TransformRequest(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/transform")
async def transform(req: TransformRequest):
    """Transform endpoint.

    If OPENAI_API_KEY is set the code attempts to call OpenAI; otherwise it returns
    a deterministic local fallback: "[local-echo] <reversed input>".
    """
    # Basic input validation
    if not req or not isinstance(req.text, str):
        raise HTTPException(status_code=400, detail="Invalid request: 'text' is required")

    key = os.environ.get("OPENAI_API_KEY", "")
    if key:
        try:
            # Import locally to avoid import-time failures when package missing
            from openai import OpenAI

            client = OpenAI(api_key=key)
            # Use chat completions if available, with defensive attribute access
            if hasattr(client, "chat") and hasattr(client.chat, "completions"):
                resp = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": req.text}],
                    max_tokens=128,
                )
                # Defensive extraction of content
                message = getattr(resp.choices[0], "message", None)
                text = getattr(message, "content", None)
                if text:
                    result = {"result": text.strip()}
                    # Apply privacy filtering if available
                    if privacy_middleware:
                        result["result"] = privacy_middleware._filter_string(result["result"])
                    return result
            # Fallback if OpenAI response shape unexpected
            logger.warning("OpenAI returned unexpected response shape, falling back")
            fallback_result = "[local-echo] " + req.text[::-1]
            if privacy_middleware:
                fallback_result = privacy_middleware._filter_string(fallback_result)
            return {"result": fallback_result}
        except Exception as e:
            logger.exception("OpenAI call failed, falling back to local echo: %s", e)
            fallback_result = "[local-echo] " + req.text[::-1]
            if privacy_middleware:
                fallback_result = privacy_middleware._filter_string(fallback_result)
            return {"result": fallback_result}
    else:
        # Deterministic local fallback
        fallback_result = "[local-echo] " + req.text[::-1]
        if privacy_middleware:
            fallback_result = privacy_middleware._filter_string(fallback_result)
        return {"result": fallback_result}
