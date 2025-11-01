"""
FastAPI WebSocket Streaming API for Echoes Research Platform

This module provides real-time streaming capabilities for research insights,
pattern detection, and truth verification using WebSocket connections.

Key Features:
- WebSocket streaming at /ws/stream
- Pattern detection with Glimpse integration
- SELF-RAG truth verification
- Real-time search and vector queries
- Rate limiting and authentication
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Import existing engines - REMOVED: RAG middleware eliminated for authentic responses
# from src.rag_orbit.retrieval import RetrievalEngine
# from src.rag_orbit.embeddings import EmbeddingEngine
# from src.rag_orbit.chunking import ChunkingEngine

# Import pattern detection
from api.pattern_detection import detect_patterns
from api.self_rag import verify_truth

# Import configuration
from api.config import get_config, setup_logging

# Import middleware
from api.middleware import setup_middleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global engines - REMOVED: No more RAG middleware for authentic responses
# retrieval_engine = None
# embedding_engine = None
# chunking_engine = None

class ConnectionManager:
    """WebSocket connection manager for real-time streaming"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Remaining: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to client: {e}")
                self.disconnect(connection)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")

# Global connection manager
manager = ConnectionManager()

# Pydantic models for API requests/responses
class PatternDetectionRequest(BaseModel):
    text: str = Field(..., description="Text to analyze for patterns")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    options: Optional[Dict[str, Any]] = Field(None, description="Detection options")

class PatternDetectionResponse(BaseModel):
    patterns: List[Dict[str, Any]] = Field(..., description="Detected patterns")
    confidence: float = Field(..., description="Overall confidence score")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# REMOVED: Search models - RAG middleware eliminated for authentic responses
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
    evidence: Optional[List[str]] = Field(None, description="Supporting evidence")
    context: Optional[Dict[str, Any]] = Field(None, description="Verification context")

class TruthVerificationResponse(BaseModel):
    verdict: str = Field(..., description="TRUE/FALSE/UNCERTAIN")
    confidence: float = Field(..., description="Confidence score 0-1")
    explanation: str = Field(..., description="Explanation of the verdict")
    evidence_used: List[str] = Field(..., description="Evidence used in verification")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - Simplified: No RAG middleware for authentic responses"""
    config = get_config()
    setup_logging(config)

    logger.info("Echoes API starting - Direct AI responses (no RAG middleware)")

    yield

    # Shutdown
    logger.info("Shutting down Echoes API...")

# Create FastAPI application
app = FastAPI(
    title="Echoes Research API",
    description="Real-time streaming API for research insights and pattern detection",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
config = get_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.security.cors_origins,
    allow_credentials=config.security.cors_allow_credentials,
    allow_methods=config.security.cors_allow_methods,
    allow_headers=config.security.cors_allow_headers,
)

# Setup additional middleware
setup_middleware(app, config)

@app.get("/health")
async def health_check():
    """Health check endpoint - Simplified: No RAG middleware"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "middleware": "none",  # Direct AI responses only
        "connections": len(manager.active_connections)
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
            # REMOVED: Search functionality - RAG middleware eliminated for authentic responses
            # elif message_type == "search":
            #     await handle_search_websocket(message, websocket)
            elif message_type == "truth_verification":
                await handle_truth_verification_websocket(message, websocket)
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

async def handle_pattern_detection_websocket(message: dict, websocket: WebSocket):
    """Handle pattern detection via WebSocket"""
    try:
        request = PatternDetectionRequest(**message.get("data", {}))

        # Send processing start notification
        await manager.send_personal_message({
            "type": "processing_start",
            "operation": "pattern_detection",
            "text_length": len(request.text)
        }, websocket)

        # Perform pattern detection (placeholder - integrate with actual Glimpse)
        patterns = await detect_patterns(request.text, request.context, request.options)

        # Send results
        response = PatternDetectionResponse(
            patterns=patterns,
            confidence=0.85  # Placeholder confidence
        )

        await manager.send_personal_message({
            "type": "pattern_detection_result",
            "data": response.dict()
        }, websocket)

    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "operation": "pattern_detection",
            "message": str(e)
        }, websocket)

async def handle_truth_verification_websocket(message: dict, websocket: WebSocket):
    """Handle truth verification via WebSocket"""
    try:
        request = TruthVerificationRequest(**message.get("data", {}))

        # Send processing start notification
        await manager.send_personal_message({
            "type": "processing_start",
            "operation": "truth_verification",
            "claim": request.claim[:100] + "..." if len(request.claim) > 100 else request.claim
        }, websocket)

        # Perform truth verification (placeholder - integrate with SELF-RAG)
        verdict = await verify_truth(request.claim, request.evidence, request.context)

        # Send results
        response = TruthVerificationResponse(
            verdict=verdict.get("verdict", "UNCERTAIN"),
            confidence=verdict.get("confidence", 0.5),
            explanation=verdict.get("explanation", "Analysis incomplete"),
            evidence_used=request.evidence or []
        )

        await manager.send_personal_message({
            "type": "truth_verification_result",
            "data": response.dict()
        }, websocket)

    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "operation": "truth_verification",
            "message": str(e)
        }, websocket)

# REST API endpoints for backward compatibility
@app.post("/api/patterns/detect", response_model=PatternDetectionResponse)
async def detect_patterns_rest(request: PatternDetectionRequest):
    """REST endpoint for pattern detection"""
    patterns = await detect_patterns(request.text, request.context, request.options)
    return PatternDetectionResponse(
        patterns=patterns,
        confidence=0.85
    )

# REMOVED: Search REST endpoint - RAG middleware eliminated for authentic responses
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
#         results=results,
#         total_found=len(results)
#     )

@app.post("/api/truth/verify", response_model=TruthVerificationResponse)
async def verify_truth_rest(request: TruthVerificationRequest):
    """REST endpoint for truth verification"""
    verdict = await verify_truth(request.claim, request.evidence, request.context)
    return TruthVerificationResponse(
        verdict=verdict.get("verdict", "UNCERTAIN"),
        confidence=verdict.get("confidence", 0.5),
        explanation=verdict.get("explanation", "Analysis incomplete"),
        evidence_used=request.evidence or []
    )

if __name__ == "__main__":
    # Get configuration
    config = get_config()

    # Start server
    uvicorn.run(
        "api.main:app",
        host=config.api.host,
        port=config.api.port,
        workers=config.api.workers,
        reload=config.api.reload,
        log_level=config.api.log_level.lower()
    )
