"""
This module implements a simple HTTP server for the MCP (Master Control Program) service.
It handles GET and POST requests, likely for managing or interacting with the AI Advisor.
"""

from typing import Optional

import uvicorn
from fastapi import FastAPI, Response
from pydantic import BaseModel

app = FastAPI(title="Local MCP Server", version="0.1.0")


# ----- Models -----
class EchoRequest(BaseModel):
    text: str
    repeat: Optional[int] = 1


class EchoResponse(BaseModel):
    echoed: str


# ----- Routes -----
@app.get("/health", status_code=200)
def health():
    """Provides a simple health check endpoint."""
    return {"status": "ok"}


@app.get("/")
def root():
    """Root endpoint with a welcome message."""
    return {"message": "MCP Server is running"}


@app.get("/favicon.ico")
def favicon():
    """Handle favicon request by returning no content."""
    return Response(status_code=204)


@app.post("/tools/echo", response_model=EchoResponse)
def echo(req: EchoRequest):
    """A simple tool that echoes back the provided text."""
    repeat_count = req.repeat if req.repeat is not None else 1
    echoed_text = " ".join([req.text] * repeat_count)
    return {"echoed": echoed_text}


# ----- Startup -----
if __name__ == "__main__":
    print("Starting local MCP server on http://127.0.0.1:8081")
    uvicorn.run(app, host="127.0.0.1", port=8081)
