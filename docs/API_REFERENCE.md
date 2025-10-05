# AI Advisor API Reference

**Version:** 0.1.0

**Base URL:** `http://localhost:8000`

## Overview

The AI Advisor API provides domain-aligned AI services with built-in safety controls:

- ✅ **Provenance Enforcement**: All assertions must cite sources
- ✅ **Human-in-the-Loop Feedback**: Continuous improvement pipeline
- ✅ **Agent Safety Layer**: Dry-run mode, kill-switch, action whitelist
- ✅ **Cross-Domain Intelligence**: Science, Commerce, Arts

## Authentication

Currently, the API is open for development. Production deployments should implement:

- JWT-based authentication
- API key validation
- Rate limiting per user/organization

## Base Endpoints

### Health Check

```http
GET /api/health
```

**Response:**

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-10-05T02:00:00Z",
  "components": {
    "api": "healthy",
    "database": "healthy",
    "feedback_queue": "healthy",
    "agent_orchestrator": "healthy"
  }
}
```

### Metrics

```http
GET /api/metrics
```

**Response:**

```json
{
  "total_requests": 1523,
  "total_assertions": 487,
  "provenance_coverage": 0.99,
  "hil_feedback_count": 52,
  "agent_executions": 234,
  "dry_run_percentage": 0.95
}
```

---

## Provenance & Assertions

### Validate Assertion

Validate that an assertion includes proper provenance.

```http
POST /api/assertions/validate
```

**Request Body:**

```json
{
  "claim": "Treatment X reduces symptoms of disease Y",
  "provenance": [
    {
      "source": "PubMed",
      "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
      "snippet": "Study demonstrates significant reduction...",
      "timestamp": "2025-10-05T00:00:00Z",
      "license": "CC-BY-4.0",
      "confidence": 0.92
    }
  ],
  "domain": "science",
  "confidence": 0.88
}
```

**Response (200 OK):**

```json
{
  "status": "ok",
  "validated_at": "2025-10-05T02:00:00Z",
  "provenance_count": 1,
  "domain": "science",
  "confidence": 0.88
}
```

**Error Response (400 Bad Request):**

```json
{
  "detail": "Missing provenance for assertion. All claims must cite sources."
}
```

**Key Features:**

- Enforces minimum 1 provenance source
- Validates timestamps are not in future
- Checks for duplicate sources (warning only)

---

## Human-in-the-Loop Feedback

### Submit Feedback

Capture user corrections and labels for model improvement.

```http
POST /api/hil/feedback
```

**Request Body:**

```json
{
  "assertion_id": "assert-12345",
  "user_id": "user-anon-678",
  "correction": "The study actually showed no significant effect",
  "label": "incorrect",
  "metadata": {
    "severity": "high",
    "domain": "science"
  },
  "timestamp": "2025-10-05T01:00:00Z"
}
```

**Response (202 Accepted):**

```json
{
  "status": "queued",
  "id": "assert-12345",
  "queue_position": 15,
  "estimated_review_time_hours": 24
}
```

**Feedback Labels:**

- `incorrect` - Factually wrong
- `biased` - Shows bias
- `helpful` - Useful and accurate
- `misleading` - Technically correct but misleading
- `incomplete` - Missing important context
- `accurate` - Fully correct

### Get Feedback List

Retrieve queued feedback for review (admin/labeler use).

```http
GET /api/hil/feedback?limit=10&status_filter=pending_review&label_filter=incorrect
```

**Query Parameters:**

- `limit` (optional): Max results, default 10
- `status_filter` (optional): Filter by status
- `label_filter` (optional): Filter by label

**Response:**

```json
{
  "total_count": 52,
  "filtered_count": 8,
  "feedback": [
    {
      "assertion_id": "assert-12345",
      "user_id": "user-anon-678",
      "correction": "...",
      "label": "incorrect",
      "metadata": {},
      "timestamp": "2025-10-05T01:00:00Z",
      "received_at": "2025-10-05T01:00:05Z",
      "status": "pending_review"
    }
  ]
}
```

---

## Agent Safety & Execution

### Execute Agent Action

Execute an agent action with safety controls.

```http
POST /api/agent/execute
```

**Request Body (Dry-Run - Default):**

```json
{
  "agent_id": "agent-001",
  "action": "search_biomedical",
  "params": {
    "query": "cancer immunotherapy",
    "max_results": 10
  },
  "dry_run": true,
  "requested_by": "user-123",
  "timeout_seconds": 30
}
```

**Response (Dry-Run):**

```json
{
  "success": true,
  "dry_run": true,
  "logs": [
    "🔒 DRY-RUN MODE: Simulated execution only (no side effects)",
    "Agent: agent-001",
    "Action: search_biomedical",
    "Parameters: {\"query\": \"cancer immunotherapy\", \"max_results\": 10}"
  ],
  "outputs": {
    "simulated": true,
    "action": "search_biomedical",
    "agent_id": "agent-001",
    "would_execute": true
  },
  "safety_checks": {
    "whitelist_ok": true,
    "dry_run_allowed": true,
    "side_effects_detected": [],
    "warnings": []
  },
  "duration_ms": 5.2
}
```

**Request Body (Real Execution):**

```json
{
  "agent_id": "agent-002",
  "action": "search_biomedical",
  "params": {"query": "..."},
  "dry_run": false,
  "requested_by": "admin-user"
}
```

**Response (Real Execution):**

```json
{
  "success": true,
  "dry_run": false,
  "logs": [
    "⚡ REAL EXECUTION MODE",
    "Agent: agent-002",
    "Action: search_biomedical",
    "Requested by: admin-user",
    "Executing action... (stub)"
  ],
  "outputs": {
    "result": "ok",
    "action": "search_biomedical",
    "executed": true
  },
  "safety_checks": {
    "whitelist_ok": true,
    "dry_run_allowed": true
  },
  "duration_ms": 152.3
}
```

**Error (403 Forbidden - Not Whitelisted):**

```json
{
  "detail": "Action 'delete_database' not whitelisted for execution"
}
```

**Whitelisted Actions:**

- `search_biomedical` - Science domain
- `simulate_economy` - Commerce domain
- `match_employment` - Commerce domain
- `generate_art` - Arts domain
- `analyze_sentiment` - General
- `no_op` - Testing only

### Kill Agent

Emergency stop for runaway agents.

```http
POST /api/agent/kill
```

**Request Body:**

```json
{
  "agent_id": "agent-002",
  "reason": "Detected infinite loop",
  "requested_by": "ops-team",
  "force": false
}
```

**Response:**
```json
{
  "status": "killed",
  "agent_id": "agent-002",
  "killed_at": "2025-10-05T02:15:00Z",
  "previous_status": "running",
  "action_interrupted": "search_biomedical",
  "force": false
}
```

**Force Kill:**

Set `"force": true` for immediate termination without cleanup.

### Get Agent Status

Check status of a running agent.

```http
GET /api/agent/status/{agent_id}
```

**Response:**

```json
{
  "agent_id": "agent-002",
  "status": {
    "action": "search_biomedical",
    "started_at": "2025-10-05T02:10:00Z",
    "status": "running"
  }
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Missing provenance for assertion"
}
```

### 403 Forbidden

```json
{
  "detail": "Action 'dangerous_action' not whitelisted for execution"
}
```

### 404 Not Found

```json
{
  "detail": "Agent agent-999 not found or not running"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "provenance"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "Provenance validation failed",
  "reason": "Assertion at index 2 missing provenance",
  "path": "/api/assertions/validate"
}
```

---

## Headers

### Request Headers

- `Content-Type: application/json` (required for POST/PUT)
- `Authorization: Bearer <token>` (when auth is enabled)

### Response Headers

- `X-Provenance-Checked: true` - Indicates provenance validation passed
- `X-Provenance-Count: 3` - Number of provenance sources found

---

## Rate Limits

**Current (Development):**

- No rate limits

**Production (Recommended):**

- 100 requests/minute per IP
- 1000 requests/hour per authenticated user
- 10 concurrent agent executions per user

---

## Examples

### cURL Examples

**Validate Assertion:**

```bash
curl -X POST http://localhost:8000/api/assertions/validate \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "Test claim",
    "provenance": [{
      "source": "PubMed",
      "timestamp": "2025-10-05T00:00:00Z"
    }]
  }'
```

**Submit Feedback:**

```bash
curl -X POST http://localhost:8000/api/hil/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "assertion_id": "test-123",
    "label": "helpful"
  }'
```

**Execute Agent (Dry-Run):**

```bash
curl -X POST http://localhost:8000/api/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "test-agent",
    "action": "no_op",
    "params": {}
  }'
```

### Python Examples

```python
import httpx

client = httpx.Client(base_url="http://localhost:8000")

# Validate assertion
response = client.post("/api/assertions/validate", json={
    "claim": "Test claim",
    "provenance": [{
        "source": "PubMed",
        "timestamp": "2025-10-05T00:00:00Z"
    }]
})
print(response.json())

# Submit feedback
response = client.post("/api/hil/feedback", json={
    "assertion_id": "test-123",
    "label": "helpful"
})
print(response.json())
```

---

## Interactive Documentation

Visit `/docs` for interactive Swagger UI documentation where you can:

- Explore all endpoints
- Try API calls directly in the browser
- See request/response schemas
- Download OpenAPI specification

---

## Support

- **Documentation**: `/docs` and `/redoc`
- **Health Check**: `/api/health`
- **Metrics**: `/api/metrics`
- **Issues**: GitHub repository
