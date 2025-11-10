"""
FastAPI WebSocket Streaming API for Echoes Research Platform

This module provides real-time streaming capabilities for research insights,
pattern detection, and truth verification using WebSocket connections.

Key Features:
- WebSocket streaming at /ws/stream
- Pattern detection with Glimpse integration
- SELF-RAG truth verification
- Real-time search and vector queries
- Direct OpenAI API connection (NO MIDDLEWARE)
"""

import json
import logging
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

# Import configuration
from api.config import get_config, setup_logging

# Import existing engines
# from src.rag_orbit.retrieval import RetrievalEngine
# from src.rag_orbit.embeddings import EmbeddingEngine
# from src.rag_orbit.chunking import ChunkingEngine
# Import pattern detection
from api.pattern_detection import detect_patterns
from api.self_rag import verify_truth

# Import selective attention utilities from consolidated module
from echoes.utils.selective_attention import (
    selective_attention,
    selective_attention_dataframe,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global engines - REMOVED: Direct connection for authentic responses
# retrieval_engine = None
# embedding_engine = None
# chunking_engine = None


class ConnectionManager:
    """WebSocket connection manager for real-time streaming"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("New WebSocket connection. Total: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.remove(websocket)
        logger.info(
            "WebSocket disconnected. Remaining: %d", len(self.active_connections)
        )

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("Failed to send message to client: %s", e)
                self.disconnect(connection)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error("Failed to send personal message: %s", e)


# Global connection manager
manager = ConnectionManager()


# Pydantic models for API requests/responses
class PatternDetectionRequest(BaseModel):
    text: str = Field(..., description="Text to analyze for patterns")
    context: dict[str, Any] | None = Field(None, description="Additional context")
    options: dict[str, Any] | None = Field(None, description="Detection options")


class PatternDetectionResponse(BaseModel):
    patterns: list[dict[str, Any]] = Field(..., description="Detected patterns")
    confidence: float = Field(..., description="Overall confidence score")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# REMOVED: Search models - Direct connection for authentic responses
# class SearchRequest(BaseModel):
#     query: str = Field(..., description="Search query")
#     top_k: int = Field(10, description="Number of results to return")
#     filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
#
# class SearchResponse(BaseModel):
#     results: List[Dict[str, Any]] = Field(..., description="Search results")
#     total_found: int = Field(..., description="Total results found")
#     timestamp: datetime = Field(default_factory=datetime.utcnow)


class TruthVerificationRequest(BaseModel):
    claim: str = Field(..., description="Claim to verify")
    evidence: list[str] | None = Field(None, description="Supporting evidence")
    context: dict[str, Any] | None = Field(None, description="Verification context")


class TruthVerificationResponse(BaseModel):
    verdict: str = Field(..., description="TRUE/FALSE/UNCERTAIN")
    confidence: float = Field(..., description="Confidence score 0-1")
    explanation: str = Field(..., description="Explanation of the verdict")
    evidence_used: list[str] = Field(..., description="Evidence used in verification")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan manager - Simplified: Direct connection for authentic responses"""
    cfg = get_config()
    try:
        import os

        if os.getenv("ECHOES_ORCHESTRAL_ENABLED", "").lower() in (
            "1",
            "true",
            "yes",
            "on",
        ):
            setattr(cfg, "orchestral_enabled", True)
    except Exception:
        pass
    setup_logging(cfg)

    logger.info("Echoes API starting - Direct connection (zero middleware)")

    yield

    # Shutdown
    logger.info("Shutting down Echoes API...")


# Create FastAPI application
app = FastAPI(
    title="Echoes Research API",
    description="Real-time streaming API for research insights and pattern detection",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Get configuration
config = get_config()

# NOTE: CORS middleware removed for direct connection
# NOTE: All middleware removed for authentic direct communication

if getattr(config, "orchestral_enabled", False):
    try:
        from api.orchestral_integration import OrchestralAPIEndpoints

        _orchestral = OrchestralAPIEndpoints()

        @app.get("/orchestral/status")
        async def orchestral_status():
            return _orchestral.get_orchestral_status()

        @app.websocket("/ws/orchestral")
        async def orchestral_websocket(websocket: WebSocket):
            await _orchestral.orchestral_websocket_endpoint(websocket)

    except Exception as e:
        logger.warning("Orchestral endpoints not available: %s", e)

# Monitoring endpoints (always on)
try:
    from api.monitoring import get_monitor_summary, get_monitor_dashboard_html

    @app.get("/monitor/summary")
    async def monitor_summary():
        return get_monitor_summary()

    # HTML dashboard is optional; disabled by default for CI/pipelines
    import os as _os

    if _os.getenv("ECHOES_MONITOR_HTML", "").lower() in ("1", "true", "yes", "on"):

        @app.get("/monitor")
        async def monitor_dashboard():
            from fastapi.responses import HTMLResponse

            return HTMLResponse(get_monitor_dashboard_html())

except Exception as e:
    logger.warning("Monitoring endpoints not available: %s", e)


@app.get("/health")
async def health_check():
    """Health check endpoint with selective attention monitoring"""
    # Only run selective attention demo if we have pandas
    try:
        import pandas as pd

        # Demonstrate selective attention with sample data
        numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        even_numbers = selective_attention(numbers)

        # Create sample dataframe for selective attention demo
        sample_data = {
            "name": ["John", "Anna", "Peter", "Linda", "James"],
            "age": [45, 22, 53, 63, 33],
            "city": ["New York", "London", "Berlin", "Sydney", "Toronto"],
        }
        sample_df = pd.DataFrame(sample_data)
        filtered_df = selective_attention_dataframe(sample_df, 50)

        demo_data = {
            "even_numbers": even_numbers,
            "filtered_people": filtered_df.to_dict("records"),
        }
    except ImportError:
        demo_data = {"error": "pandas not available for demo"}

    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "direct_connection": "selective_attention_enabled",
        "connections": len(manager.active_connections),
        "selective_attention_demo": demo_data,
    }


@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time streaming"""
    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Process based on message type
            message_type = message.get("type", "unknown")

            if message_type == "pattern_detection":
                await handle_pattern_detection_websocket(message, websocket)
            # REMOVED: Search functionality - Direct connection for authentic responses
            # elif message_type == "search":
            #     await handle_search_websocket(message, websocket)
            elif message_type == "truth_verification":
                await handle_truth_verification_websocket(message, websocket)
            else:
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                    },
                    websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error: %s", e)
        manager.disconnect(websocket)


async def handle_pattern_detection_websocket(message: dict, websocket: WebSocket):
    """Handle pattern detection via WebSocket"""
    try:
        request = PatternDetectionRequest(**message.get("data", {}))

        # Send processing start notification
        await manager.send_personal_message(
            {
                "type": "processing_start",
                "operation": "pattern_detection",
                "text_length": len(request.text),
            },
            websocket,
        )

        # Perform pattern detection (placeholder - integrate with actual Glimpse)
        patterns = await detect_patterns(request.text, request.context, request.options)

        # Send results
        response = PatternDetectionResponse(
            patterns=patterns,
            confidence=0.85,  # Placeholder confidence
        )

        await manager.send_personal_message(
            {"type": "pattern_detection_result", "data": response.dict()}, websocket
        )

    except Exception as e:
        await manager.send_personal_message(
            {"type": "error", "operation": "pattern_detection", "message": str(e)},
            websocket,
        )


async def handle_truth_verification_websocket(message: dict, websocket: WebSocket):
    """Handle truth verification via WebSocket"""
    try:
        request = TruthVerificationRequest(**message.get("data", {}))

        # Send processing start notification
        await manager.send_personal_message(
            {
                "type": "processing_start",
                "operation": "truth_verification",
                "claim": request.claim[:100] + "..."
                if len(request.claim) > 100
                else request.claim,
            },
            websocket,
        )

        # Perform truth verification (placeholder - integrate with SELF-RAG)
        verdict = await verify_truth(request.claim, request.evidence, request.context)

        # Send results
        response = TruthVerificationResponse(
            verdict=verdict.get("verdict", "UNCERTAIN"),
            confidence=verdict.get("confidence", 0.5),
            explanation=verdict.get("explanation", "Analysis incomplete"),
            evidence_used=request.evidence or [],
        )

        await manager.send_personal_message(
            {"type": "truth_verification_result", "data": response.dict()}, websocket
        )

    except Exception as e:
        await manager.send_personal_message(
            {"type": "error", "operation": "truth_verification", "message": str(e)},
            websocket,
        )


"""REST API endpoints with caching"""


# REST API endpoints for backward compatibility
@app.post("/api/patterns/detect", response_model=PatternDetectionResponse)
async def detect_patterns_rest(request: PatternDetectionRequest):
    """REST endpoint for pattern detection"""
    patterns = await detect_patterns(request.text, request.context, request.options)
    return PatternDetectionResponse(patterns=patterns, confidence=0.85)


# REMOVED: Search REST endpoint - Direct connection for authentic responses
# @app.post("/api/search", response_model=SearchResponse)
# async def search_rest(request: SearchRequest):
#     """REST endpoint for search"""
#     if retrieval_engine:
#         results = await retrieval_engine.search(
#             query=request.query,
#             top_k=request.top_k,
#             filters=request.filters
#         )
#     else:
#         results = []
#
#     return SearchResponse(
@app.post("/api/truth/verify", response_model=TruthVerificationResponse)
async def verify_truth_rest(request: TruthVerificationRequest):
    """REST endpoint for truth verification"""
    verdict = await verify_truth(request.claim, request.evidence, request.context)
    return TruthVerificationResponse(
        verdict=verdict.get("verdict", "UNCERTAIN"),
        confidence=verdict.get("confidence", 0.5),
        explanation=verdict.get("explanation", "Analysis incomplete"),
        evidence_used=request.evidence or [],
    )


# Single app instance is configured above; no duplicate app factory.

if __name__ == "__main__":
    # Get configuration
    config = get_config()

    # Setup logging
    setup_logging(config)

    # Start the server
    uvicorn.run(
        "api.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.reload,
        log_level=config.logging.level.lower(),
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
