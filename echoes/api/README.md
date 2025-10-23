# Echoes AI Assistant API

A RESTful API for multimodal AI processing with webhook support, built on FastAPI.

## 🚀 Features

- **🖼️ Image Analysis**: GPT-4o Vision-powered image understanding
- **🎵 Audio Transcription**: OpenAI Whisper for speech-to-text
- **🔄 Auto-Detection**: Smart media type detection and processing
- **🪝 Webhook Support**: Real-time event notifications
- **🔐 Authentication**: API key-based security
- **⏱️ Rate Limiting**: Configurable usage limits
- **💰 Cost Tracking**: Automatic expense monitoring
- **📊 Analytics**: Usage statistics and insights

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Required Python packages (see `requirements.txt`)

## 🛠️ Installation

1. **Install dependencies:**
   ```bash
   cd echoes/api
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Configure API keys:**
   Edit `.env` file:
   ```env
   OPENAI_API_KEY=your-openai-api-key
   ECHOES_API_KEYS=user1-key-qwerty123456:1000/hour,user2-key-456:500/hour
   ```

## 🚀 Quick Start

### Development Mode
```bash
python start_dev.py
```

### Production Mode
```bash
python start_prod.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Authentication

All API requests require an API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/health
```

### Endpoints

#### Health Check
```http
GET /health
```

#### Image Analysis
```http
POST /api/v1/analyze/image
POST /api/v1/analyze/image/upload
```

**Request Body:**
```json
{
  "image_url": "https://example.com/image.jpg",
  "custom_prompt": "Describe this image in detail",
  "webhook_url": "https://your-app.com/webhook"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "analysis": "Detailed image description...",
    "image_info": {
      "dimensions": "1920x1080",
      "format": "JPEG"
    },
    "processing_cost": 0.0049
  },
  "request_id": "img_1234567890",
  "processing_time": 2.34
}
```

#### Audio Transcription
```http
POST /api/v1/transcribe/audio
POST /api/v1/transcribe/audio/upload
```

**Request Body:**
```json
{
  "audio_url": "https://example.com/audio.mp3",
  "webhook_url": "https://your-app.com/webhook"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transcription": "Full audio transcription text...",
    "audio_info": {
      "duration_formatted": "00:15:00",
      "language": "english"
    },
    "processing_cost": 0.0901
  },
  "request_id": "audio_1234567890",
  "processing_time": 3.21
}
```

#### Media Auto-Processing
```http
POST /api/v1/process/media
```

**Request Body:**
```json
{
  "media_url": "https://example.com/file.jpg",
  "analysis_type": "auto",
  "custom_prompt": "Analyze this media file",
  "webhook_url": "https://your-app.com/webhook"
}
```

#### Webhook Management
```http
POST /api/v1/webhooks/register
GET /api/v1/webhooks/list
DELETE /api/v1/webhooks/{webhook_id}
```

**Register Webhook:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["image_processed", "audio_transcribed"],
  "secret": "optional-webhook-secret"
}
```

#### Analytics
```http
GET /api/v1/analytics
```

## 🪝 Webhook Integration

### Supported Events
- `image_processed` - Image analysis completed
- `audio_transcribed` - Audio transcription completed
- `media_processed` - Media auto-processing completed
- `*_error` - Processing errors

### Webhook Payload
```json
{
  "event": "image_processed",
  "request_id": "img_1234567890",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "analysis": "Image analysis results...",
    "processing_cost": 0.0049
  }
}
```

### Webhook Security
- Optional HMAC-SHA256 signature verification
- Configurable secrets per webhook
- Signature in `X-Webhook-Signature` header

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ECHOES_API_HOST` | `0.0.0.0` | Server host |
| `ECHOES_API_PORT` | `8000` | Server port |
| `ECHOES_API_DEBUG` | `false` | Debug mode |
| `ECHOES_API_KEYS` | `dev-key-qwerty123456:1000/hour` | API keys with limits |
| `ECHOES_RATE_LIMIT_REQUESTS` | `100` | Requests per window |
| `ECHOES_RATE_LIMIT_WINDOW` | `3600` | Rate limit window (seconds) |
| `ECHOES_MAX_FILE_SIZE` | `26214400` | Max file size (25MB) |
| `ECHOES_ENABLE_CORS` | `true` | Enable CORS |
| `ECHOES_TRUSTED_HOSTS` | `*` | Trusted hosts |

### API Keys Format
```
ECHOES_API_KEYS=key1:limit1,key2:limit2
# Examples:
# user1-key:1000/hour
# premium-key:10000/day
# unlimited-key:unlimited
```

## 📊 Cost Tracking

The API automatically tracks usage costs:

- **Images**: $0.001275 per 512×512 low detail
- **Audio**: $0.006 per minute (Whisper)
- **Analytics**: Access via `/api/v1/analytics`

## 🔧 Development

### Project Structure
```
echoes/api/
├── server.py          # Main FastAPI application
├── requirements.txt   # Python dependencies
├── .env.example       # Environment template
├── start_dev.py       # Development startup
├── start_prod.py      # Production startup
└── README.md          # This file
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### API Documentation
When running the server, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🛡️ Security

- API key authentication required
- Rate limiting per API key
- File size validation
- CORS configuration
- Trusted host validation
- No server information disclosure

## 📈 Performance

- Async processing with background tasks
- Automatic file cleanup
- Connection pooling with httpx
- Optimized for concurrent requests
- Production-ready with multiple workers

## 🤝 Integration Examples

### JavaScript/Node.js
```javascript
const response = await fetch('/api/v1/analyze/image', {
  method: 'POST',
  headers: {
    'X-API-Key': 'your-api-key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    image_url: 'https://example.com/image.jpg'
  })
});

const result = await response.json();
```

### Python
```python
import requests

response = requests.post('/api/v1/transcribe/audio',
  headers={'X-API-Key': 'your-api-key'},
  json={'audio_url': 'https://example.com/audio.mp3'}
)

result = response.json()
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/process/media" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"media_url": "https://example.com/file.jpg"}'
```

## 📞 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review server logs for errors
3. Verify API key configuration
4. Check rate limits and costs

## 📄 License

This project is part of the Echoes AI Assistant system.
