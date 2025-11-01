# Glimpse Performance Playbook

## Overview
This playbook captures performance tuning decisions, configurations, and SLAs for the Glimpse Glimpse when using OpenAI API samplers. It is intended for developers, operators, and anyone optimizing latency, throughput, or reliability.

## 1. Latency Thresholds (LatencyMonitor)

| Threshold | Default (ms) | Purpose | Calibration |
|-----------|--------------|---------|--------------|
| t1 | 1500 | Show “trying” status message | Based on observed OpenAI p50~1.4s |
| t2 | 2500 | Add intent-matching message | Around p75 for OpenAI |
| t3 | 4000 | Patience hinge (UI choices) | Near p95 |
| t4 | 6000 | Degraded notice | Extreme tail; p99+ |

**How to adjust:**  
```python
monitor = LatencyMonitor(t1=1200, t2=2200, t3=3500, t4=5500)
engine = GlimpseEngine(latency_monitor=monitor)
```

## 2. Caching (PromptCache)

- **Type:** LRU + TTL
- **Default max size:** 2000 entries (increased from 1000)
- **Default TTL:** 7200 s (2 hours, increased from 1 hour)
- **Keying:** SHA‑256 of `[messages, model, temperature, max_tokens]`
- **Hit rate target:** >30% in mixed workloads; >70% where prompts repeat

**Configuration:**
```python
from glimpse.cache_helpers import PromptCache
cache = PromptCache(max_size=2000, ttl_seconds=7200)
# Use via @cached_openai_call(cache) decorator
```

**Observed impact (benchmark):**
- Cache hit: ~0.06 s
- Cache miss: ~1.7 s
- ~27× speedup for repeated prompts

## 2.1. Default Sampler Selection

The Glimpse defaults to the OpenAI-backed sampler when available. Control via environment variable:

```bash
export GLIMPSE_USE_OPENAI=true   # default: use OpenAI sampler
export GLIMPSE_USE_OPENAI=false  # force local fallback sampler
```

If the OpenAI sampler fails to import or is disabled, the Glimpse gracefully falls back to the local default sampler.

## 3. Retry & Backoff

- **Max attempts:** 5 (configurable)
- **Base delay:** 0.5 s
- **Backoff:** exponential (2^n) with jitter up to 50%
- **Max delay:** 60 s
- **Retry on:** RateLimitError, most OpenAIError types

**Usage:** `call_with_backoff(fn, *args, max_attempts=5, base_delay=0.5, max_delay=60.0, **kwargs)`

## 4. Error Mapping (Sampler)

| OpenAI Exception | Mapped GlimpseResult status | Fallback behavior |
|-------------------|-----------------------------|-------------------|
| RateLimitError | `rate_limited` | Essence-only fallback |
| AuthenticationError | `auth_error` | Error essence only |
| BadRequestError | `bad_request` | Error essence only |
| NotFoundError | `not_found` | Error essence only |
| UnprocessableEntityError | `unprocessable` | Error essence only |
| PermissionError | `permission_denied` | Error essence only |
| InternalServerError | `server_error` | Essence-only fallback |
| Other | `error` | Essence-only fallback |

**Essence-only fallback** extracts up to 8 meaningful tokens from input/goal, returns a minimal essence string with status annotation.

## 5. Batching Strategy

- **Current implementation:** Concurrent execution with semaphore (max 5) – not true API batching.
- **Eligibility heuristic:** Same goal+constraints across drafts and total input < 4000 characters.
- **When to use:** When many similar drafts arrive within a short window (e.g., bulk summarization tasks).
- **Future:** Consider OpenAI batch endpoints or multi-turn prompts to reduce per-request overhead.

## 6. Observed SLAs (Benchmarks)

| Metric | Value | Notes |
|--------|-------|-------|
| Avg latency (cache miss) | ~1.7 s | OpenAI gpt-4o-mini, 256 max tokens |
| Avg latency (cache hit) | ~0.06 s | In-memory LRU cache |
| Throughput (single thread) | ~0.6 req/s (misses) / ~16 req/s (hits) | |
| Tail latency (p95) | ~2.5 s | Aligns with t2 threshold |
| Cache hit rate (mixed) | 45% | Improves with repetition |
| Concurrent batch latency (3) | 3.24 s total (~1.08 s per) | Limited by API rate limits |

## 7. Tuning Checklist

- [ ] Adjust `LatencyMonitor` thresholds if using a different model or region.
- [ ] Increase `PromptCache` size/TTL for workloads with high repetition.
- [ ] Tune `call_with_backoff` `max_attempts` and `base_delay` if rate limits are frequent.
- [ ] Enable structured logging (`openai_call`, `openai_rate_limit_retry`, etc.) for observability.
- [ ] Run `glimpse/load_test_openai.py` after any config change to validate SLAs.
- [ ] Monitor `cache.get_hit_rate()` and error rates in production.

## 8. Load Testing

Run the load test to validate under concurrency:
```bash
python -m glimpse.load_test_openai
```
Adjust `concurrent_users` and `requests_per_user` to match expected traffic.

## 9. Monitoring & Alerting

- **Latency alerts:** If median or p95 exceeds t2/t3 for sustained periods.
- **Cache hit rate alert:** If below 20% in repetitive workloads.
- **Error rate alert:** If >5% of requests result in `rate_limited`, `server_error`, or `error`.

## 10. Future Optimizations

- True API batching via OpenAI batch endpoints.
- Model-specific tuning (e.g., gpt-4o vs gpt-4o-mini latency profiles).
- Dynamic cache sizing based on memory pressure.
- Request deduplication across concurrent identical drafts.
- Adaptive sampler selection (fast local fallback vs OpenAI).

---

**Version:** 1.0  
**Last updated:** 2025-10-29  
**Maintainers:** Glimpse dev team
