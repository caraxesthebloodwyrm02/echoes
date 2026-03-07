# AGENTS.md

**FastAPI Architecture Design Guide for AI Agents**
**Version:** 2026.03 (Updated March 2026)
**Purpose:** This file is the single source of truth for any AI agent (Grok, Claude, Cursor, etc.) working on Python + FastAPI projects.
It enforces production-grade architectural decisions, especially for **resilience patterns** (inbound rate limiting + outbound retry/circuit-breaker logic to handle and mitigate 429 errors).

Follow the **Chronological Step-by-Step Routine** on every new service or major refactor.
Always reference the embedded **Architecture Decision Template** (Section 4).
This document is derived from live 2026 community consensus (FastAPI Best Architecture repos, SlowApi dominance, layered/Clean patterns).

**Workspace:** For .gitignore, env docs, and shared QA conventions, align with **E:\\Seeds\\ECOSYSTEM_BASELINE.md**.

## 1. Core Principles (Never Violate)
- Async-first (Python 3.11+, FastAPI ≥0.115, httpx.AsyncClient)
- Layered separation: Routers → Services → CRUD/Repository → Models/DB
- Resilience by default: Never let one 429 cascade
- Observability: Prometheus metrics + structured logging on every rate-limit/retry event
- Testability: Full DI + dependency injection for everything

## 2. Recommended Project Structure (2026 Standard – Layered / Pseudo-3-Tier)
```bash
project-root/
├── app/
│   ├── main.py
│   ├── core/              # config.py, security.py, logging.py
│   ├── api/
│   │   └── v1/
│   │       ├── routers/   # feature-based (users/, payments/)
│   │       └── dependencies.py
│   ├── schemas/           # Pydantic DTOs
│   ├── services/          # business logic + outbound calls
│   ├── crud/              # or repositories/ (DB ops)
│   ├── models/            # SQLAlchemy / ORM
│   ├── db/                # session.py, migrations/
│   └── resilience/        # rate_limit.py, retry_utils.py, circuit_breaker.py
├── tests/
├── alembic/
├── .env.example
├── pyproject.toml         # uv / poetry
├── Dockerfile
└── docker-compose.yml     # Redis, Postgres, etc.
```

## 3. Chronological Step-by-Step Routine for Designing a Python-FastAPI Architecture
Follow **exactly in order**. Each step includes decision support, known issues, and debugging capabilities.

### Step 1: Requirements & Scope (15 min)
- Classify: Inbound 429 (protect your API) vs Outbound 429 (you call external APIs).
- Estimate scale: <5k rpm → in-memory OK; >10k rpm → Redis + edge gateway mandatory.
- **Decision support:** Public API? Start with Cloudflare/Nginx rate limiting.
- **Known issue:** Ignoring scale leads to thundering herd on retries.
- **Debug tip:** Add a quick `locust` load test script in this phase.

### Step 2: Choose Architecture Pattern
- Default (most projects): Layered (Routers → Services → CRUD).
- Large/DDD: Clean/Hexagonal (ports & adapters).
- **Known issue:** Monolithic main.py becomes untestable after ~20 endpoints.
- **Debug tip:** Run `pytest --cov` early; >70% coverage target.

### Step 3: Core Setup & DI
- Use `pydantic-settings` + `fastapi.Depends`.
- Initialize Redis (aioredis) if distributed.

### Step 4: Implement Inbound Rate Limiting
- **Mandatory library (2026):** `slowapi` (dominant, 1.9k+ stars).
- Follow Architecture Decision Template (Section 4).
- **Known issue:** Using IP-only key on authenticated APIs → unfair bans.
- **Debug tip:** Set `app.state.limiter` and test with `curl -H "X-API-Key:..."`.

### Step 5: Implement Outbound Resilience (Retries + Circuit Breaker)
- Retries: `tenacity` + `wait_exponential_jitter`.
- Circuit breaker: Custom middleware or `pybreaker` (dedicated FastAPI libs are niche).
- Wrap every external call in `services/`.
- **Known issue:** No jitter → all clients retry at the same second (thundering herd).
- **Debug tip:** Force 429 responses in tests with `respx`.

### Step 6: Observability & Error Handling
- Add Prometheus middleware + custom 429 handler.
- Log with `structlog` (include `retry_attempt`, `wait_time`, `client_key`).

### Step 7: Security & Edge Layers
- API keys / JWT in dependencies.
- Rate-limit login endpoints stricter (brute-force protection).

### Step 8: Testing Strategy
- Unit: `pytest` + `respx` for 429 simulation.
- Integration: Docker Compose with Redis.
- Load: `locust` + rate-limit exhaustion tests.

### Step 9: Documentation & OpenAPI
- Document rate limits in responses schema (`429` + `Retry-After`).
- Add `/health` and `/metrics` endpoints.

### Step 10: Deployment & Monitoring
- Docker + Redis.
- Alert on rate-limit hit rate >5%.
- Review: Re-run this routine on every major feature.

## 4. Architecture Decision Template (Reference This for 429 Handling)
**Context & Scope**
- Inbound 429 (your API) → clean 429 + headers.
- Outbound 429 (external calls) → retry + backoff + fallback.
- Scale: Single instance? Distributed? Edge first?

**Decision Matrix (2026)**

| Requirement               | Recommended (Default)          | Alternative                     | Avoid                          |
|---------------------------|--------------------------------|---------------------------------|--------------------------------|
| Inbound rate limiting     | **SlowApi + Redis**            | fastapi-limiter (simple cases)  | fastapi-advanced-rate-limiter  |
| Outbound retries          | **tenacity + httpx.AsyncClient + jitter** | aiolimiter (throttling)     | Manual loops                   |
| Circuit breaker           | Custom or pybreaker            | circuit_breaker_fastapi (niche) | None                           |
| Distributed               | Redis backend                  | In-memory (dev only)            | Pure in-memory in prod         |
| High scale (>10k rpm)     | Cloudflare/Nginx + app         | App only                        | App only for public APIs       |

**Default Implementation Skeleton** (copy-paste ready)
```python
# app/resilience/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request, HTTPException

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Per-route example
@app.get("/expensive")
@limiter.limit("10/minute", key_func=lambda r: r.headers.get("X-API-Key", "anon"))
async def protected():
    data = await resilient_call("https://external-api.com")
    return data
```

**Outbound Resilience** (in services/)
```python
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
import httpx

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=1, max=30),
    retry=retry_if_exception_type(httpx.HTTPStatusError),
    reraise=True
)
async def resilient_call(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()
```

**Best Practices Checklist** (tick before commit)
- [ ] SlowApi + Redis for inbound
- [ ] `Retry-After` + `X-RateLimit-*` headers
- [ ] Exponential jitter on outbound retries
- [ ] Async everywhere
- [ ] Prometheus metrics on 429 hits
- [ ] Per-user / tiered limits in Redis
- [ ] Edge gateway for >10k rpm

## 5. Known Issues & Debugging Capabilities (Decision Support)
| Issue | Symptom | Root Cause (2026) | Fix & Debugging Command |
|-------|---------|-------------------|-------------------------|
| Blocking event loop | High latency under load | Sync Redis in middleware | Switch to `aioredis`; test with `uvicorn --workers 4` |
| Thundering herd | All clients retry at once | No jitter on tenacity | Add `wait_exponential_jitter`; monitor with Prometheus |
| Unfair rate limiting | Legit users blocked | IP-only key on auth APIs | Use `X-API-Key` or JWT subject as key_func |
| 429 not respected upstream | Cascading failures | Ignoring `Retry-After` header | Parse header in tenacity `before_sleep` hook |
| Test flakiness | Intermittent 429 in CI | Shared Redis state | Use `pytest-redis` fixture or in-memory for tests |
| Observability gap | Can't trace rate-limit spikes | No metrics | Add `prometheus-fastapi-instrumentator` |

## 6. How to Use This File as an Agent
- When user says "design FastAPI service", start with: "Following AGENTS.md routine Step 1..."
- Always output the Decision Matrix and Checklist in your final architecture proposal.
- If requirements change, re-run the full 10-step routine and explain deviations.

**Last updated:** March 2026 (SlowApi confirmed dominant, layered architecture consensus).  
**Agents:** When in doubt, ask the human for scale numbers or external API list before Step 4.

---

Copy this file into the root of any FastAPI repo.  
AI agents will now automatically follow production-grade resilience patterns and avoid the outdated/hallucinated libraries from older templates.

Need a full boilerplate repo generated from this AGENTS.md? Just say the word.

## 7. Circuit Breaker Patterns (Expanded Guide for FastAPI 2026)

This is a **drop-in replacement / expansion** for the brief mention in your AGENTS.md (replace the old "Circuit breaker" line in the Decision Matrix and add this as **new Section 7** right after the Inbound/Outbound sections).

It follows the same style: chronological decision support, production patterns, 429-specific guidance, known issues, and debugging capabilities. All recommendations are validated against live 2026 community consensus (pybreaker dominance in official guides, Redis-backed state for distributed services, tight integration with tenacity).

### 7.1 Theory – The Three States (Never Skip This Explanation)
The Circuit Breaker pattern (inspired by Michael Nygard's *Release It!*) acts like an electrical breaker for your external calls:

- **Closed** (default): Normal traffic flows. Every failure is counted.
- **Open** (tripped): Fast-fail immediately (no timeouts, no hammering). Return fallback or 503. Prevents cascading failures and retry storms.
- **Half-Open** (testing recovery): After `reset_timeout`, a single test request is allowed. Success → back to Closed. Failure → Open again.

### 7.2 Why This Is Critical for 429 Mitigation in FastAPI
When external APIs (LLM providers, payment gateways, third-party services) start returning 429s:
- Pure tenacity retries alone can create **thundering herds** and amplify rate-limit exhaustion.
- A circuit breaker trips on repeated 429/5xx → your service stops calling the failing endpoint entirely.
- You instantly degrade gracefully (cached response, default data, queue for later) instead of 500-ing your users.

### 7.3 Library Recommendation (2026 Consensus)
**Primary Choice**: `pybreaker` (danielfm/pybreaker)
- Mature, battle-tested, excellent Redis storage support (`CircuitRedisStorage`).
- Works seamlessly with async FastAPI + httpx + tenacity.
- Built-in listeners for Prometheus/structured logging.

**Alternatives** (only when justified):
- `aiobreaker` / `fastapi-cb` (pure async fork) – good for ultra-simple async-only projects.
- Custom lightweight class – acceptable for <5 external services.
- `circuit_breaker_fastapi` (middleware) – niche, low adoption; avoid unless you want global middleware behavior.

**Installation** (add to pyproject.toml):
```toml
pybreaker = "^1.0"
redis = {extras = ["asyncio"], version = "^5.2"}
```

### 7.4 Implementation in Your Layered Architecture
Place breakers in `app/resilience/circuit_breakers.py` and inject them into services (never in routers or middleware).

**app/resilience/circuit_breakers.py**
```python
import pybreaker
from redis.asyncio import Redis
from pybreaker import CircuitBreaker, CircuitRedisStorage

class ExternalServiceBreakers:
    """One breaker per external service – different thresholds per SLA."""

    def __init__(self, redis_client: Redis):
        storage = CircuitRedisStorage(pybreaker.STATE_CLOSED, redis_client)

        self.payment = CircuitBreaker(
            fail_max=5,
            reset_timeout=60,
            state_storage=storage,
            name="payment-service",
            listeners=[PrometheusListener()]  # custom listener (see below)
        )

        self.llm_api = CircuitBreaker(
            fail_max=8,          # higher for flaky LLM providers
            reset_timeout=30,
            state_storage=storage,
            name="external-llm",
            exclude=[ValueError]  # don't trip on business errors
        )
```

**Custom listener for observability** (add to same file):
```python
class PrometheusListener(pybreaker.CircuitBreakerListener):
    def state_change(self, cb, old_state, new_state):
        # Increment Prometheus gauge: circuit_breaker_state{name=cb.name, state=new_state}
        logger.info(f"Circuit {cb.name} changed {old_state} → {new_state}")
```

**Usage in Services Layer** (perfect 429 pattern):
```python
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
import httpx
from app.resilience.circuit_breakers import external_breakers

class ExternalAPIService:
    def __init__(self, breakers: ExternalServiceBreakers):
        self.breakers = breakers

    async def call_llm(self, prompt: str):
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential_jitter(initial=1, max=15),
            retry=retry_if_exception_type(httpx.HTTPStatusError),  # only retry 429/5xx
            reraise=True
        )
        @self.breakers.llm_api   # ← circuit breaker decorator
        async def _protected_call():
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post("https://api.llm-provider.com/generate", json=...)
                if r.status_code == 429:
                    # Respect upstream Retry-After if present
                    retry_after = int(r.headers.get("Retry-After", 30))
                    raise httpx.HTTPStatusError(...)  # will be caught by breaker
                r.raise_for_status()
                return r.json()

        try:
            return await _protected_call()
        except pybreaker.CircuitBreakerError:
            # Circuit OPEN → graceful degradation
            logger.warning("LLM circuit breaker OPEN – serving fallback")
            return await self.get_cached_or_degraded_response(prompt)
```

**Dependency injection** (in `app/api/dependencies.py`):
```python
def get_breakers(redis=Depends(get_redis)):
    return ExternalServiceBreakers(redis)
```

### 7.5 Updated Decision Matrix Snippet (add to Section 4)
| Requirement          | Recommended (Default 2026)       | Alternative              | Avoid                  |
|----------------------|----------------------------------|--------------------------|------------------------|
| Circuit Breaker      | **pybreaker + Redis storage**    | aiobreaker / custom      | circuit_breaker_fastapi (niche) |
| Integration          | Decorator in Services layer      | FastAPI dependency       | Global middleware only |
| With Retries         | Tenacity inside Closed state     | Pure breaker             | No retries at all      |

### 7.6 Best Practices Checklist (tick before every merge)
- [ ] One dedicated breaker per external service/API
- [ ] Redis-backed storage in production (shared state across instances)
- [ ] Always implement fallback on `CircuitBreakerError`
- [ ] Combine with tenacity + `Retry-After` header parsing
- [ ] Exclude business exceptions from failure count
- [ ] Prometheus metrics on state changes + failure counts
- [ ] Document fallback behavior in OpenAPI spec

### 7.7 Known Issues & Debugging Capabilities
| Issue                          | Symptom                              | Root Cause                     | Debug / Fix Command |
|--------------------------------|--------------------------------------|--------------------------------|---------------------|
| Breaker never closes           | Stuck in Open forever                | Too aggressive fail_max        | Check logs for `state_change`, increase reset_timeout |
| Thundering herd on Half-Open   | All instances recover at once        | No shared Redis state          | Switch to `CircuitRedisStorage` |
| Trips on transient 429s        | Over-sensitive on rate limits        | fail_max too low               | Raise to 8–10 for LLM APIs; add jitter |
| Async blocking                 | High latency under load              | Sync Redis client              | Use `redis.asyncio` + async wrapper |
| No observability               | Can't see why users get degraded     | Missing listener               | Add PrometheusListener + Grafana alert |
| Fallback not implemented       | 500 instead of graceful degrade      | Caught only generic Exception  | Explicit `except pybreaker.CircuitBreakerError` |

**Pro Tip for 429-heavy services (LLMs, external AI)**: Use a shorter `reset_timeout` (15–30s) and higher `fail_max` so the breaker recovers quickly once the upstream quota resets.

---

**How to integrate into AGENTS.md**  
1. Paste this entire section as **Section 7**.  
2. Update the original Step 5 bullet to: "Outbound resilience: tenacity + pybreaker circuit breakers".  
3. Re-run the full 10-step routine on any service that calls external rate-limited APIs.
