"""
Echoes AI Assistant API Server
============================

RESTful API for multimodal processing with webhook support.

Features:
- Image analysis using GPT-4o Vision
- Audio transcription using OpenAI Whisper
- Webhook support for automated processing
- Authentication and security measures
- Rate limiting and usage tracking

Endpoints:
- POST /api/v1/analyze/image - Analyze images
- POST /api/v1/transcribe/audio - Transcribe audio files
- POST /api/v1/process/media - Auto-detect and process media files
- POST /api/v1/webhooks/register - Register webhook endpoints
- GET /api/v1/webhooks/list - List registered webhooks
- GET /api/v1/analytics - Get usage analytics

Authentication:
- API Key authentication required for all endpoints
- Rate limiting based on API key usage
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import tempfile
import base64
import httpx
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks, UploadFile, File, Form
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field, validator
import uvicorn
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Import Echoes components
from assistant_v2_core import EchoesAssistantV2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# API Key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Global variables
assistant: Optional[EchoesAssistantV2] = None
api_keys: Dict[str, Dict[str, Any]] = {}
webhooks: Dict[str, Dict[str, Any]] = {}


class APIConfig:
    """API Configuration settings."""

    def __init__(self):
        self.host = os.getenv("ECHOES_API_HOST", "0.0.0.0")
        self.port = int(os.getenv("ECHOES_API_PORT", "8000"))
        self.debug = os.getenv("ECHOES_API_DEBUG", "false").lower() == "true"
        self.max_file_size = int(os.getenv("ECHOES_MAX_FILE_SIZE", "26214400"))  # 25MB
        self.rate_limit_requests = int(os.getenv("ECHOES_RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("ECHOES_RATE_LIMIT_WINDOW", "3600"))  # 1 hour
        self.enable_cors = os.getenv("ECHOES_ENABLE_CORS", "true").lower() == "true"
        self.trusted_hosts = os.getenv("ECHOES_TRUSTED_HOSTS", "*").split(",")


# Initialize configuration
config = APIConfig()


# Pydantic models for API requests/responses
class ImageAnalysisRequest(BaseModel):
    """Request model for image analysis."""

    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    custom_prompt: Optional[str] = None
    webhook_url: Optional[str] = None

    @validator("image_base64")
    def validate_base64(cls, v):
        if v and not v.startswith(("data:image/", "iVBORw0KGgo=")):  # Basic validation
            raise ValueError("Invalid base64 image data")
        return v


class AudioTranscriptionRequest(BaseModel):
    """Request model for audio transcription."""

    audio_url: Optional[str] = None
    audio_base64: Optional[str] = None
    webhook_url: Optional[str] = None


class MediaProcessingRequest(BaseModel):
    """Request model for general media processing."""

    media_url: Optional[str] = None
    media_base64: Optional[str] = None
    analysis_type: Optional[str] = None  # 'image', 'audio', or auto-detect
    custom_prompt: Optional[str] = None
    webhook_url: Optional[str] = None


class WebhookRegistration(BaseModel):
    """Model for webhook registration."""

    url: str = Field(..., description="Webhook URL to receive notifications")
    events: List[str] = Field(
        ..., description="Events to trigger webhook: ['image_processed', 'audio_transcribed', 'media_processed']"
    )
    secret: Optional[str] = Field(None, description="Webhook secret for signature verification")
    active: bool = Field(True, description="Whether webhook is active")


class APIResponse(BaseModel):
    """Standard API response model."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    request_id: Optional[str] = None
    processing_time: Optional[float] = None


class WebhookPayload(BaseModel):
    """Webhook payload model."""

    event: str
    request_id: str
    timestamp: datetime
    data: Dict[str, Any]
    signature: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global assistant

    # Startup
    logger.info("🚀 Starting Echoes API Server...")
    try:
        # Initialize Echoes Assistant
        assistant = EchoesAssistantV2(
            enable_rag=False,  # Disable RAG for API mode
            enable_tools=False,  # Disable tools for API mode
            enable_status=False,  # Disable status for API mode
        )
        logger.info("✅ Echoes Assistant initialized")

        # Load API keys from environment
        load_api_keys()

        # Load webhooks from storage
        load_webhooks()

        logger.info("🎉 API Server ready!")

    except Exception as e:
        logger.error(f"❌ Failed to initialize API server: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down Echoes API Server...")


def load_api_keys():
    """Load API keys from environment or config file."""
    global api_keys

    # Load from environment variables
    api_key_env = os.getenv("ECHOES_API_KEYS", "")
    if api_key_env:
        for key_value in api_key_env.split(","):
            if ":" in key_value:
                key, limits = key_value.split(":", 1)
                api_keys[key.strip()] = {"limits": limits.strip(), "created_at": datetime.now(), "active": True}

    # Default API key for development
    if not api_keys and config.debug:
        api_keys["dev-key-qwerty123456"] = {"limits": "1000/hour", "created_at": datetime.now(), "active": True}
        logger.warning("⚠️ Using default development API key: dev-key-qwerty123456")


def load_webhooks():
    """Load webhooks from storage."""
    global webhooks
    # In a production system, this would load from a database
    # For now, we'll keep them in memory
    pass


def verify_api_key(api_key: str = Depends(api_key_header)):
    """Verify API key and return key info."""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    if api_key not in api_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")

    key_info = api_keys[api_key]
    if not key_info.get("active", False):
        raise HTTPException(status_code=401, detail="API key deactivated")

    return {"key": api_key, "info": key_info}


# Create FastAPI app
app = FastAPI(
    title="Echoes AI Assistant API",
    description="RESTful API for multimodal processing with webhook support",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add CORS
if config.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add trusted host middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=config.trusted_hosts)


# Webhook management functions
async def trigger_webhook(webhook_url: str, payload: WebhookPayload, secret: Optional[str] = None):
    """Trigger a webhook with the given payload."""
    try:
        headers = {"Content-Type": "application/json"}
        if secret:
            # In production, create proper signature
            headers["X-Webhook-Signature"] = f"sha256={secret}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(webhook_url, json=payload.dict(), headers=headers)
            response.raise_for_status()
            logger.info(f"✅ Webhook triggered successfully: {webhook_url}")

    except Exception as e:
        logger.error(f"❌ Webhook failed: {webhook_url} - {e}")


async def process_with_webhook(request_func, webhook_url: Optional[str], event_type: str, request_id: str):
    """Process a request and trigger webhook if provided."""
    try:
        # Process the request
        result = await request_func()

        # Trigger webhook if provided
        if webhook_url:
            payload = WebhookPayload(event=event_type, request_id=request_id, timestamp=datetime.now(), data=result)
            # Run webhook in background
            asyncio.create_task(trigger_webhook(webhook_url, payload))

        return result

    except Exception as e:
        # Trigger error webhook if provided
        if webhook_url:
            error_payload = WebhookPayload(
                event=f"{event_type}_error", request_id=request_id, timestamp=datetime.now(), data={"error": str(e)}
            )
            asyncio.create_task(trigger_webhook(webhook_url, error_payload))
        raise


# API Endpoints will be added in the next part...


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now(), "version": "1.0.0"}


# Image Analysis Endpoints
@app.post("/api/v1/analyze/image", response_model=APIResponse)
@limiter.limit(f"{config.rate_limit_requests} per {config.rate_limit_window} seconds")
async def analyze_image(
    request: Request,
    req: ImageAnalysisRequest,
    background_tasks: BackgroundTasks,
    api_key_info: dict = Depends(verify_api_key),
):
    """Analyze an image using GPT-4o Vision."""
    import time

    start_time = time.time()
    request_id = f"img_{int(time.time() * 1000)}"

    try:
        if not assistant:
            raise HTTPException(status_code=503, detail="Assistant not initialized")

        # Download image if URL provided
        image_path = None
        if req.image_url:
            # Download image from URL
            async with httpx.AsyncClient() as client:
                response = await client.get(req.image_url)
                response.raise_for_status()

                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                    temp_file.write(response.content)
                    image_path = temp_file.name

        elif req.image_base64:
            # Decode base64 image
            if req.image_base64.startswith("data:image/"):
                # Remove data URL prefix
                header, data = req.image_base64.split(",", 1)
                image_data = base64.b64decode(data)
            else:
                image_data = base64.b64decode(req.image_base64)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                temp_file.write(image_data)
                image_path = temp_file.name

        else:
            raise HTTPException(status_code=400, detail="Either image_url or image_base64 must be provided")

        # Analyze image
        import asyncio

        async def process_image():
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: assistant.analyze_image(image_path, req.custom_prompt))
            # Clean up temp file
            try:
                os.unlink(image_path)
            except:
                pass
            return result

        # Process with webhook support
        if req.webhook_url:
            background_tasks.add_task(
                process_with_webhook, process_image, req.webhook_url, "image_processed", request_id
            )
            return APIResponse(
                success=True,
                data={"message": "Image analysis started, results will be sent to webhook"},
                request_id=request_id,
                processing_time=time.time() - start_time,
            )
        else:
            result = await process_image()
            return APIResponse(
                success=result.get("success", False),
                data=result if result.get("success") else None,
                error=result.get("error") if not result.get("success") else None,
                request_id=request_id,
                processing_time=time.time() - start_time,
            )

    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        return APIResponse(success=False, error=str(e), request_id=request_id, processing_time=time.time() - start_time)


# Audio Transcription Endpoints
@app.post("/api/v1/transcribe/audio", response_model=APIResponse)
@limiter.limit(f"{config.rate_limit_requests} per {config.rate_limit_window} seconds")
async def transcribe_audio(
    request: Request,
    req: AudioTranscriptionRequest,
    background_tasks: BackgroundTasks,
    api_key_info: dict = Depends(verify_api_key),
):
    """Transcribe audio using OpenAI Whisper."""
    import time

    start_time = time.time()
    request_id = f"audio_{int(time.time() * 1000)}"

    try:
        if not assistant:
            raise HTTPException(status_code=503, detail="Assistant not initialized")

        # Download audio if URL provided
        audio_path = None
        if req.audio_url:
            # Download audio from URL
            async with httpx.AsyncClient() as client:
                response = await client.get(req.audio_url)
                response.raise_for_status()

                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                    temp_file.write(response.content)
                    audio_path = temp_file.name

        elif req.audio_base64:
            # Decode base64 audio
            audio_data = base64.b64decode(req.audio_base64)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(audio_data)
                audio_path = temp_file.name

        else:
            raise HTTPException(status_code=400, detail="Either audio_url or audio_base64 must be provided")

        # Transcribe audio
        async def process_audio():
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: assistant.transcribe_audio(audio_path))
            # Clean up temp file
            try:
                os.unlink(audio_path)
            except:
                pass
            return result

        # Process with webhook support
        if req.webhook_url:
            background_tasks.add_task(
                process_with_webhook, process_audio, req.webhook_url, "audio_transcribed", request_id
            )
            return APIResponse(
                success=True,
                data={"message": "Audio transcription started, results will be sent to webhook"},
                request_id=request_id,
                processing_time=time.time() - start_time,
            )
        else:
            result = await process_audio()
            return APIResponse(
                success=result.get("success", False),
                data=result if result.get("success") else None,
                error=result.get("error") if not result.get("success") else None,
                request_id=request_id,
                processing_time=time.time() - start_time,
            )

    except Exception as e:
        logger.error(f"Audio transcription error: {e}")
        return APIResponse(success=False, error=str(e), request_id=request_id, processing_time=time.time() - start_time)


# General Media Processing Endpoint
@app.post("/api/v1/process/media", response_model=APIResponse)
@limiter.limit(f"{config.rate_limit_requests} per {config.rate_limit_window} seconds")
async def process_media(
    request: Request,
    req: MediaProcessingRequest,
    background_tasks: BackgroundTasks,
    api_key_info: dict = Depends(verify_api_key),
):
    """Auto-detect and process media files."""
    import time

    start_time = time.time()
    request_id = f"media_{int(time.time() * 1000)}"

    try:
        if not assistant:
            raise HTTPException(status_code=503, detail="Assistant not initialized")

        # Download media if URL provided
        media_path = None
        if req.media_url:
            # Download media from URL
            async with httpx.AsyncClient() as client:
                response = await client.get(req.media_url)
                response.raise_for_status()

                # Determine file extension from content type
                content_type = response.headers.get("content-type", "")
                ext = ".bin"  # default
                if "image/" in content_type:
                    ext = ".jpg"
                elif "audio/" in content_type:
                    ext = ".mp3"

                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                    temp_file.write(response.content)
                    media_path = temp_file.name

        elif req.media_base64:
            # Decode base64 media
            media_data = base64.b64decode(req.media_base64)

            # Auto-detect type from base64 prefix if present
            ext = ".bin"
            if req.media_base64.startswith("data:image/"):
                ext = ".jpg"
            elif req.media_base64.startswith("data:audio/"):
                ext = ".mp3"

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                temp_file.write(media_data)
                media_path = temp_file.name

        else:
            raise HTTPException(status_code=400, detail="Either media_url or media_base64 must be provided")

        # Process media
        async def process_media_file():
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: assistant.analyze_media_file(media_path, req.analysis_type, req.custom_prompt)
            )
            # Clean up temp file
            try:
                os.unlink(media_path)
            except:
                pass
            return result

        # Process with webhook support
        if req.webhook_url:
            background_tasks.add_task(
                process_with_webhook, process_media_file, req.webhook_url, "media_processed", request_id
            )
            return APIResponse(
                success=True,
                data={"message": "Media processing started, results will be sent to webhook"},
                request_id=request_id,
                processing_time=time.time() - start_time,
            )
        else:
            result = await process_media_file()
            return APIResponse(
                success=result.get("success", False),
                data=result if result.get("success") else None,
                error=result.get("error") if not result.get("success") else None,
                request_id=request_id,
                processing_time=time.time() - start_time,
            )

    except Exception as e:
        logger.error(f"Media processing error: {e}")
        return APIResponse(success=False, error=str(e), request_id=request_id, processing_time=time.time() - start_time)


# Webhook Management Endpoints
@app.post("/api/v1/webhooks/register", response_model=APIResponse)
async def register_webhook(webhook: WebhookRegistration, api_key_info: dict = Depends(verify_api_key)):
    """Register a webhook for event notifications."""
    import uuid

    webhook_id = str(uuid.uuid4())

    webhooks[webhook_id] = {
        "id": webhook_id,
        "url": webhook.url,
        "events": webhook.events,
        "secret": webhook.secret,
        "active": webhook.active,
        "created_at": datetime.now(),
        "api_key": api_key_info["key"],
    }

    return APIResponse(success=True, data={"webhook_id": webhook_id, "message": "Webhook registered successfully"})


@app.get("/api/v1/webhooks/list", response_model=APIResponse)
async def list_webhooks(api_key_info: dict = Depends(verify_api_key)):
    """List registered webhooks for the API key."""
    user_webhooks = [
        {k: v for k, v in webhook.items() if k != "secret"}
        for webhook in webhooks.values()
        if webhook["api_key"] == api_key_info["key"]
    ]

    return APIResponse(success=True, data={"webhooks": user_webhooks})


@app.delete("/api/v1/webhooks/{webhook_id}", response_model=APIResponse)
async def delete_webhook(webhook_id: str, api_key_info: dict = Depends(verify_api_key)):
    """Delete a registered webhook."""
    if webhook_id not in webhooks:
        raise HTTPException(status_code=404, detail="Webhook not found")

    webhook = webhooks[webhook_id]
    if webhook["api_key"] != api_key_info["key"]:
        raise HTTPException(status_code=403, detail="Access denied")

    del webhooks[webhook_id]

    return APIResponse(success=True, data={"message": "Webhook deleted successfully"})


# Analytics Endpoint
@app.get("/api/v1/analytics", response_model=APIResponse)
async def get_analytics(api_key_info: dict = Depends(verify_api_key)):
    """Get usage analytics and cost information."""
    if not assistant:
        raise HTTPException(status_code=503, detail="Assistant not initialized")

    analytics = assistant.get_cost_analytics()

    return APIResponse(success=True, data=analytics)


# File Upload Endpoints (alternative to base64/URL methods)
@app.post("/api/v1/analyze/image/upload", response_model=APIResponse)
async def analyze_image_upload(
    file: UploadFile = File(...),
    custom_prompt: Optional[str] = Form(None),
    webhook_url: Optional[str] = Form(None),
    api_key_info: dict = Depends(verify_api_key),
):
    """Analyze an uploaded image file."""
    import time

    start_time = time.time()
    request_id = f"img_upload_{int(time.time() * 1000)}"

    try:
        if not assistant:
            raise HTTPException(status_code=503, detail="Assistant not initialized")

        # Validate file size
        file_content = await file.read()
        if len(file_content) > config.max_file_size:
            raise HTTPException(status_code=413, detail=f"File too large. Maximum size: {config.max_file_size} bytes")

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(file_content)
            image_path = temp_file.name

        # Analyze image
        result = assistant.analyze_image(image_path, custom_prompt)

        # Clean up temp file
        try:
            os.unlink(image_path)
        except:
            pass

        # Trigger webhook if provided
        if webhook_url and result.get("success"):
            payload = WebhookPayload(
                event="image_processed", request_id=request_id, timestamp=datetime.now(), data=result
            )
            asyncio.create_task(trigger_webhook(webhook_url, payload))

        return APIResponse(
            success=result.get("success", False),
            data=result if result.get("success") else None,
            error=result.get("error") if not result.get("success") else None,
            request_id=request_id,
            processing_time=time.time() - start_time,
        )

    except Exception as e:
        logger.error(f"Image upload analysis error: {e}")
        return APIResponse(success=False, error=str(e), request_id=request_id, processing_time=time.time() - start_time)


@app.post("/api/v1/transcribe/audio/upload", response_model=APIResponse)
async def transcribe_audio_upload(
    file: UploadFile = File(...), webhook_url: Optional[str] = Form(None), api_key_info: dict = Depends(verify_api_key)
):
    """Transcribe an uploaded audio file."""
    import time

    start_time = time.time()
    request_id = f"audio_upload_{int(time.time() * 1000)}"

    try:
        if not assistant:
            raise HTTPException(status_code=503, detail="Assistant not initialized")

        # Validate file size
        file_content = await file.read()
        if len(file_content) > config.max_file_size:
            raise HTTPException(status_code=413, detail=f"File too large. Maximum size: {config.max_file_size} bytes")

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(file_content)
            audio_path = temp_file.name

        # Transcribe audio
        result = assistant.transcribe_audio(audio_path)

        # Clean up temp file
        try:
            os.unlink(audio_path)
        except:
            pass

        # Trigger webhook if provided
        if webhook_url and result.get("success"):
            payload = WebhookPayload(
                event="audio_transcribed", request_id=request_id, timestamp=datetime.now(), data=result
            )
            asyncio.create_task(trigger_webhook(webhook_url, payload))

        return APIResponse(
            success=result.get("success", False),
            data=result if result.get("success") else None,
            error=result.get("error") if not result.get("success") else None,
            request_id=request_id,
            processing_time=time.time() - start_time,
        )

    except Exception as e:
        logger.error(f"Audio upload transcription error: {e}")
        return APIResponse(success=False, error=str(e), request_id=request_id, processing_time=time.time() - start_time)


if __name__ == "__main__":
    uvicorn.run("server:app", host=config.host, port=config.port, reload=config.debug, log_level="info")
