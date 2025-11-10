#!/usr/bin/env python3
"""
FastAPI + Archer Framework Integration

This demo shows how to integrate the Archer Framework with Echoes FastAPI server
using uvicorn for web-based communication management.
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

import uvicorn
from communication import (ArcherFramework, CommunicationMessage,
                           CommunicationType, create_communicator)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# Pydantic models for API
class MessageRequest(BaseModel):
    content: Any = Field(..., description="Message content")
    sender: str = Field(default="web_client", description="Sender identifier")
    receiver: str = Field(..., description="Receiver identifier")
    message_type: str = Field(default="network", description="Communication type")
    priority: int = Field(default=5, ge=1, le=10, description="Priority level (1-10)")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class MessageResponse(BaseModel):
    success: bool
    message: str
    message_id: str
    response_time: float
    error_code: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MetricsResponse(BaseModel):
    metrics: dict[str, float]
    total_messages: int
    active_communicators: int


class CommunicatorConfig(BaseModel):
    communicator_type: str
    config: dict[str, Any] = Field(default_factory=dict)


# Initialize FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the Archer Framework on startup"""
    initialize_default_communicators()
    print("🚀 Archer Framework API started successfully!")
    print("📡 Available endpoints:")
    print("   POST /send-message - Send a message")
    print("   GET /metrics - Get performance metrics")
    print("   GET /history - Get message history")
    print("   POST /register-communicator - Register new communicator")
    print("   GET /communicators - List active communicators")
    yield
    print("🔌 Archer Framework API shutting down...")


app = FastAPI(
    title="Archer Framework API",
    description="Advanced Communication System for Echoes Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Global Archer Framework instance
archer_framework = ArcherFramework()


# Initialize default communicators
def initialize_default_communicators():
    """Initialize default communicators for the API"""

    # Network communicator (for demonstration)
    network_comm = create_communicator(
        CommunicationType.NETWORK,
        {"host": "localhost", "port": 8080, "protocol": "tcp"},
    )
    archer_framework.register_communicator(CommunicationType.NETWORK, network_comm)

    # IPC communicator
    ipc_comm = create_communicator(CommunicationType.INTERPROCESS, {"method": "queue"})
    archer_framework.register_communicator(CommunicationType.INTERPROCESS, ipc_comm)

    # Psychological communicator
    psych_comm = create_communicator(
        CommunicationType.PSYCHOLOGICAL, {"style": "assertive", "ei_level": 0.8}
    )
    archer_framework.register_communicator(CommunicationType.PSYCHOLOGICAL, psych_comm)

    # Physics communicator
    physics_comm = create_communicator(
        CommunicationType.PHYSICS, {"medium": "air", "frequency": 2.4e9, "power": 1.0}
    )
    archer_framework.register_communicator(CommunicationType.PHYSICS, physics_comm)

    # Programmatic communicator
    prog_comm = create_communicator(CommunicationType.PROGRAMMATIC)
    archer_framework.register_communicator(CommunicationType.PROGRAMMATIC, prog_comm)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Archer Framework API",
        "description": "Advanced Communication System for Echoes Platform",
        "version": "1.0.0",
        "endpoints": [
            "/send-message",
            "/metrics",
            "/history",
            "/register-communicator",
            "/communicators",
        ],
    }


@app.post("/send-message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    """Send a message using the Archer Framework"""
    try:
        # Convert string to CommunicationType enum
        try:
            comm_type = CommunicationType(request.message_type.lower())
        except ValueError:
            available_types = [t.value for t in CommunicationType]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid communication type. Available: {available_types}",
            )

        # Create message
        message = CommunicationMessage(
            content=request.content,
            sender=request.sender,
            receiver=request.receiver,
            message_type=comm_type,
            priority=request.priority,
            metadata=request.metadata,
        )

        # Send message
        result = archer_framework.send_message(message)

        return MessageResponse(
            success=result.success,
            message=result.message,
            message_id=message.id,
            response_time=result.response_time,
            error_code=result.error_code,
            metadata=result.metadata,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get performance metrics from the Archer Framework"""
    try:
        metrics = archer_framework.get_metrics()
        total_messages = len(archer_framework.message_history)
        active_communicators = len(archer_framework.communicators)

        return MetricsResponse(
            metrics=metrics,
            total_messages=total_messages,
            active_communicators=active_communicators,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_message_history(limit: int = 50, offset: int = 0):
    """Get message history with pagination"""
    try:
        history = archer_framework.message_history
        total = len(history)

        # Apply pagination
        paginated_history = history[offset : offset + limit]

        # Convert to dict format
        history_data = []
        for message in paginated_history:
            history_data.append(
                {
                    "id": message.id,
                    "content": message.content,
                    "sender": message.sender,
                    "receiver": message.receiver,
                    "timestamp": message.timestamp,
                    "message_type": message.message_type.value,
                    "priority": message.priority,
                    "checksum": message.checksum,
                    "metadata": message.metadata,
                }
            )

        return {
            "messages": history_data,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/register-communicator")
async def register_communicator(config: CommunicatorConfig):
    """Register a new communicator"""
    try:
        # Convert string to CommunicationType enum
        try:
            comm_type = CommunicationType(config.communicator_type.lower())
        except ValueError:
            available_types = [t.value for t in CommunicationType]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid communication type. Available: {available_types}",
            )

        # Create communicator
        communicator = create_communicator(comm_type, config.config)
        archer_framework.register_communicator(comm_type, communicator)

        return {
            "success": True,
            "message": f"Successfully registered {config.communicator_type} communicator",
            "communicator_type": config.communicator_type,
            "config": config.config,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/communicators")
async def list_communicators():
    """List all active communicators"""
    try:
        communicators = []
        for comm_type, comm in archer_framework.communicators.items():
            communicators.append(
                {
                    "type": comm_type.value,
                    "class": comm.__class__.__name__,
                    "is_active": comm.is_active,
                    "config": comm.config,
                }
            )

        return {"communicators": communicators, "total": len(communicators)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test-psychological-analysis")
async def test_psychological_analysis():
    """Test psychological communication analysis"""
    try:
        test_messages = [
            "I understand your perspective and would like to share my thoughts",
            "This situation is frustrating and needs immediate attention",
            "I feel excited about the opportunity to collaborate on this project",
            "Whatever you think is best, I don't really have an opinion",
            "You're wrong and this is how we're going to do it!",
        ]

        results = []
        for content in test_messages:
            message = CommunicationMessage(
                content=content,
                sender="test_user",
                receiver="system",
                message_type=CommunicationType.PSYCHOLOGICAL,
            )

            result = archer_framework.send_message(message)
            results.append(
                {
                    "content": content,
                    "success": result.success,
                    "metadata": result.metadata,
                }
            )

        return {"test_results": results, "total_tested": len(test_messages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test-physics-simulation")
async def test_physics_simulation():
    """Test physics signal transmission simulation"""
    try:
        test_scenarios = [
            {"medium": "air", "frequency": 2.4e9, "power": 1.0, "distance": 100},
            {"medium": "cable", "frequency": 1e6, "power": 5.0, "distance": 1000},
            {"medium": "fiber", "frequency": 1.55e9, "power": 10.0, "distance": 10000},
            {"medium": "vacuum", "frequency": 5e9, "power": 0.1, "distance": 1000},
        ]

        results = []
        for scenario in test_scenarios:
            message = CommunicationMessage(
                content="Signal data packet",
                sender="transmitter",
                receiver="receiver",
                message_type=CommunicationType.PHYSICS,
                metadata=scenario,
            )

            result = archer_framework.send_message(message)
            results.append(
                {
                    "scenario": scenario,
                    "success": result.success,
                    "metadata": result.metadata,
                }
            )

        return {"simulation_results": results, "total_scenarios": len(test_scenarios)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_server():
    """Run the FastAPI server with uvicorn"""
    print("🌐 Starting Archer Framework FastAPI Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📖 API docs available at: http://localhost:8000/docs")
    print("🔄 Interactive docs at: http://localhost:8000/redoc")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info")


if __name__ == "__main__":
    run_server()
