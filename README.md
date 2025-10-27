# EchoesAssistantV2: Enterprise Multimodal AI Platform

**Transforming AI assistants into programmable multimodal platforms**
> **Consent-Based License**: This project requires explicit consent for use. Please read the [LICENSE](LICENSE) file and contact the licensor for usage terms.
>
> We look for clusters of order in noisy data. When signals don't repeat or break known physics, we pause and observe. Dormant is a pause for clarity, not a failure.

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)

A production-ready, enterprise-grade AI assistant platform featuring advanced multimodal processing capabilities, RESTful API integration, and comprehensive automation features.

## 🚀 Key Features

### 🤖 Core AI Assistant
- **Advanced RAG System**: Semantic knowledge retrieval with FAISS-based vector search and OpenAI embeddings
- **Tool Integration**: 50+ built-in tools for enhanced capabilities
- **Context Management**: Persistent conversation history and memory
- **Streaming Responses**: Real-time response generation

### 🖼️ Multimodal Processing
- **Image Analysis**: GPT-4o Vision-powered visual intelligence
- **Audio Transcription**: OpenAI Whisper speech-to-text processing
- **Auto-Detection**: Smart media type recognition and processing

### 🌐 RESTful API Platform
- **21+ Endpoints**: Comprehensive API for integration
- **Webhook Automation**: Real-time event-driven processing
- **API Key Authentication**: Enterprise-grade security
- **Rate Limiting**: Configurable usage controls
- **Cost Tracking**: Real-time expense monitoring

### 🐳 Production Ready
- **Docker Containerization**: Multi-stage builds with security hardening
- **Load Balancing**: Multi-worker production setup
- **Health Monitoring**: Built-in health checks and metrics
- **Comprehensive Documentation**: Complete deployment guides

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Architecture](#-architecture)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

## 🏃 Quick Start

### Local Development
```bash
# Clone the repository
git clone https://github.com/caraxesthebloodwyrm02/echoes.git
cd echoes

# Set up environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp echoes/api/.env.example echoes/api/.env
# Edit .env with your OpenAI API key

# (Optional) Configure OpenAI embeddings RAG preset
# See docs/RAG_OPENAI_MIGRATION.md for openai-* presets

# Run development server
python echoes/api/start_dev.py
```

### Docker Deployment
```bash
# Set OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Deploy with Docker
cd echoes/api
docker-compose up -d

# API available at http://localhost:8000
curl http://localhost:8000/health
```

## 📚 API Documentation

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /health` | Health check | System status monitoring |
| `GET /api/v1/analytics` | Usage analytics | Cost and performance metrics |
| `POST /api/v1/analyze/image` | Image analysis | GPT-4o Vision processing |
| `POST /api/v1/transcribe/audio` | Audio transcription | Whisper speech-to-text |
| `POST /api/v1/process/media` | Auto-processing | Smart media detection |
| `POST /api/v1/webhooks/*` | Webhook management | Automation triggers |

### Authentication
```bash
# All API requests require authentication
curl -H "X-API-Key: your-api-key" \
     http://localhost:8000/api/v1/analytics
```

### Interactive Documentation
When running the API server, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### RAG with OpenAI Embeddings
Configure OpenAI-embeddings RAG presets:
- **Migration Guide**: See `docs/RAG_OPENAI_MIGRATION.md`
- **Presets**: `openai-fast`, `openai-balanced`, `openai-accurate`
- **Usage**: `EchoesAssistantV2(rag_preset='openai-balanced')`
- **Bulk Loading**: See `docs/LANGCHAIN_RAG_LOADER.md` for LangChain integration
#### Scientific Validation API (research-only)

- `GET /api/v1/research/license` – read the research-only license
- `POST /api/v1/research/token` – request a research token (institution + purpose)
- `POST /api/v1/validate/sensory` – validate signals using physics guardrails, sidechain smoothing, consensus, and optional 7-scenario benchmark

See docs/SCIENTIFIC_API_REFERENCE.md for plain-language details.

## 🏗️ Architecture

```
EchoesAssistantV2/
├── assistant_v2_core.py      # Core AI assistant engine
├── echoes/
│   ├── api/                  # REST API implementation
│   │   ├── server.py        # FastAPI application (26k+ lines)
│   │   ├── Dockerfile       # Container configuration
│   │   └── docker-compose.yml # Orchestration
│   └── core/                # Multimodal processing
│       ├── multimodal_processor.py  # OpenAI integrations
│       ├── cost_optimizer.py       # Usage optimization
│       └── rag_v2.py              # Enhanced RAG system
├── tools/                   # Tool framework (50+ tools)
├── app/                     # Action execution system
├── data/                    # Persistent storage
└── docs/                    # Comprehensive documentation
```

### Key Components

- **🤖 Assistant Core**: Advanced RAG with tool integration
- **🖼️ Multimodal Processor**: Image/audio processing pipeline
- **🌐 API Server**: FastAPI-based REST endpoints
- **🔧 Tool Registry**: Extensible tool framework
- **💾 Memory Store**: Conversation persistence
- **📊 Analytics Engine**: Cost and usage tracking

## 🚀 Deployment

### Production Setup
```bash
# 1. Environment configuration
export OPENAI_API_KEY="your-production-key"
export ECHOES_API_KEYS="prod-key-secure:1000/hour"

# 2. Docker deployment
cd echoes/api
docker-compose -f docker-compose.yml up -d

# 3. Verify deployment
docker-compose ps
curl http://your-server:8000/health
```

### Scaling Configuration
```yaml
# docker-compose.yml scaling
services:
  echoes-api:
    deploy:
      replicas: 3
    environment:
      - ECHOES_API_HOST=0.0.0.0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

### Cloud Deployment
The API is ready for deployment on:
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **Kubernetes clusters**
- **DigitalOcean App Platform**

## 💻 Development

### Prerequisites
- Python 3.11+
- OpenAI API key
- Docker (optional)

### Project Structure
```
├── echoes/api/              # REST API implementation
├── echoes/core/             # Core processing components
├── tools/                   # Tool framework
├── app/                     # Action execution
├── tests/                   # Test suite
├── docs/                    # Documentation
└── scripts/                 # Utility scripts
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run full test suite
pytest tests/ -v

# Run specific API tests
pytest tests/ -k "api" -v
```

### Code Quality
```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy .
```

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
    image_url: 'https://example.com/image.jpg',
    custom_prompt: 'Describe this image'
  })
});
```

### Python
```python
import requests

response = requests.post('/api/v1/transcribe/audio',
  headers={'X-API-Key': 'your-api-key'},
  json={'audio_url': 'https://example.com/audio.mp3'}
)

result = response.json()
print(f"Transcription: {result['data']['transcription']}")
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/process/media" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"media_url": "https://example.com/file.jpg"}'
```

## 🔐 Security

- **API Key Authentication**: Required for all endpoints
- **Rate Limiting**: Configurable per-key limits
- **Input Validation**: Comprehensive request validation
- **CORS Configuration**: Configurable cross-origin settings
- **HTTPS Enforcement**: Production SSL/TLS support
- **Audit Logging**: Complete request/response logging
  
Research-only safeguards:
- **Research Tokens**: Access to validation endpoints requires institution+purpose tokens
- **Physics Guardrails**: Wavelength/temperature ranges, Wien’s consistency, visible-band checks
- **Sidechain Smoothing**: Reduces spikes to reveal repeating patterns
- **Consensus Verdicts**: Multi-domain votes; forwarding only when physics is active and consensus is sufficient
- **Encryption**: AES-GCM requests/responses and webhooks; set ECHOES_ENCRYPTION_FORCE=true in production

## 📊 Cost Optimization

The platform includes built-in cost optimization features:

- **Usage Analytics**: Real-time cost tracking
- **Smart Caching**: Response caching to reduce API calls
- **Batch Processing**: Efficient bulk operations
- **Rate Optimization**: Intelligent request pacing

## 🧪 Testing & Validation

### Automated Testing
```bash
# Run all tests
pytest tests/ -v

# API integration tests
pytest tests/ -k "integration" -v

# Performance benchmarks
pytest tests/ -k "performance" --benchmark
```

### Manual Testing
```bash
# Health check
curl http://localhost:8000/health

# API key validation
curl -H "X-API-Key: test-key" http://localhost:8000/api/v1/analytics

# Image processing test
curl -X POST http://localhost:8000/api/v1/analyze/image \
  -H "X-API-Key: test-key" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://picsum.photos/512/512"}'
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Format code: `black . && ruff check .`
6. Submit a pull request

## 📄 License

This project uses a **Consent-Based License** that requires explicit permission for use. Before using, modifying, or distributing this software, you must:

1. Read the complete [LICENSE](LICENSE) file
2. Contact the licensor (Erfan Kabir) at irfankabir02@gmail.com
3. Obtain explicit written consent for your intended use case

### Key Requirements:
- **Consent Required**: No usage without explicit approval
- **Ethical Principles**: Adherence to responsible use guidelines
- **Use Case Declaration**: Clear description of intended application
- **Revocable**: License can be withdrawn at any time

**Contact**: Erfan Kabir (irfankabir02@gmail.com) | GitHub: [@caraxesthebloodwyrm02](https://github.com/caraxesthebloodwyrm02)

---

## 🙏 Acknowledgements

We extend our deepest gratitude to all who have contributed to this project. See [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md) for detailed recognition of contributors, technologies, and inspirations that made Echoes possible.

**Special Thanks:**
- **OpenAI** for GPT-4o Vision and Whisper APIs
- **FastAPI** framework for the API foundation
- **FAISS** for efficient vector search
- **The open source community** for incredible tools and libraries

---

**EchoesAssistantV2**: Transforming AI assistants into programmable multimodal platforms through responsible innovation.

**🌟 Ready for ethical deployment worldwide! 🚀**
