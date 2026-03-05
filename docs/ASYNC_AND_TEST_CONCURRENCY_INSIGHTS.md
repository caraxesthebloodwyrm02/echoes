# Async/await and test concurrency – insights and patterns

Summary of where async is used in Echoes and how to use test/concurrency output as data for resolution and debugging.

## Where async/await appears

| Area | Files (representative) | Role |
|------|------------------------|------|
| **API** | `api/main.py`, `api/middleware.py`, `api/dependencies.py` | FastAPI async route handlers, middleware, DI |
| **Core** | `assistant_v2_core.py` | Async assistant methods and streaming |
| **Glimpse** | `glimpse/engine.py`, `glimpse/openai_wrapper.py`, `glimpse/rate_limiter.py`, `glimpse/performance_optimizer.py`, `glimpse/alignment.py`, `glimpse/cache_helpers.py`, `glimpse/batch_helpers.py` | Async LLM calls, batching, rate limiting, alignment |
| **Resilience** | `app/resilience/rate_limit.py`, `app/resilience/retry_utils.py`, `app/resilience/circuit_breakers.py` | Async rate limit, retry, circuit breaker |
| **Accounting/Tab** | `misc/Accounting/tab/__init__.py`, `misc/Accounting/tab/sync_engine/__init__.py` | Async sync and interaction processing |
| **Tools** | `tools/glimpse_tools.py` | Async tool execution |
| **Tests** | `tests/glimpse/test_*.py`, `tests/test_rate_limiter.py`, `tests/test_model_router.py`, `app/resilience/tests/*` | Async tests (e.g. `@pytest.mark.asyncio`) |

## Patterns useful for resolution

1. **Entry points**: Scripts and demos often use `asyncio.run(main())`; the event loop is created there. Concurrency issues (e.g. “event loop closed” or callbacks after shutdown) usually stem from mixing sync code with async or from creating multiple loops.
2. **FastAPI**: All route handlers are async; ensure any blocking call is offloaded (e.g. `run_in_executor`) or replaced with an async equivalent so the event loop is not blocked.
3. **Glimpse**: The glimpse engine and OpenAI wrapper use async for HTTP and batching. Rate limiting and caching are async; tests in `tests/glimpse/` are the main place to observe concurrent behavior and flakiness.
4. **Resilience**: Retries and circuit breakers wrap async calls; test with `app/resilience/tests/` and watch for timeouts or repeated failures under load.

## Using test results and concurrency output as data

- **Run tests with structured output**  
  `pytest tests/ -v --tb=short -q` (or `-v --tb=long` for full tracebacks). Capture stdout/stderr to a file and inspect for:
  - Order-dependent or flaky tests (e.g. “passed” then “failed” on rerun).
  - Timeouts or “event loop is closed” in async tests.
  - Slow tests that might be contending on shared resources.

- **Focus on async tests**  
  `pytest tests/ -v -k "asyncio or glimpse or rate_limiter or retry" --tb=short` to exercise async and resilience paths. Use the output to see which coroutines or endpoints are slow or failing.

- **Benchmarks**  
  `tests/benchmark_rate_limiter.py` and scripts under `glimpse/benchmark_*.py` exercise concurrency and rate limits. Their output (throughput, latency, errors) is the “data” for tuning limits and detecting regressions.

- **Resolution workflow**  
  1. Run the relevant test subset and save the log.  
  2. Identify failing or slow cases and whether they are async (e.g. `async def test_...`).  
  3. Check for shared state (e.g. global rate limiter, shared client) or synchronous blocking in async code.  
  4. Fix by aligning async/await usage (no blocking in async functions), or by giving tests isolated state (e.g. fresh client or rate limiter per test).

## Quick reference

- **Async tests**: Use `@pytest.mark.asyncio` and `async def test_...`; ensure `pytest-asyncio` is installed and configured (e.g. in `pytest.ini` or `pyproject.toml`).
- **Concurrency**: Most concurrency is cooperative (single-threaded event loop). For CPU-heavy work, use `asyncio.to_thread()` or `run_in_executor` so the loop stays responsive.
- **Test output as baseline**: After fixing flaky or slow tests, re-run and store a short “known good” log (e.g. in `docs/` or CI artifacts) to compare against future runs.
