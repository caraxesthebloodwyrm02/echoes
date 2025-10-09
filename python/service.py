from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import logging

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
                    return {"result": text.strip()}
            # Fallback if OpenAI response shape unexpected
            logger.warning("OpenAI returned unexpected response shape, falling back")
            return {"result": "[local-echo] " + req.text[::-1]}
        except Exception as e:
            logger.exception("OpenAI call failed, falling back to local echo: %s", e)
            return {"result": "[local-echo] " + req.text[::-1]}
    else:
        # Deterministic local fallback
        return {"result": "[local-echo] " + req.text[::-1]}
