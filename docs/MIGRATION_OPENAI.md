# OpenAI API alignment (Echoes)

This document anchors repository decisions to **official OpenAI documentation**. Re-verify links and dates when bumping the `openai` SDK (`pyproject.toml` currently pins `openai>=2.33.0,<3.0.0`).

## Platform timeline (Assistants API)

Public guidance indicates the **Assistants API** (assistants / threads / runs) is deprecated in favor of the **Responses API** and related patterns. Community and docs commonly cite a **shutdown window around August 2026**—confirm on the current **Deprecations** page before planning hard cutovers:

- [Deprecations](https://developers.openai.com/api/docs/deprecations)
- [Migrate to the Responses API](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [Assistants migration guide](https://developers.openai.com/api/docs/guides/assistants/migration) (for codebases that used threads/runs)

## Reality check: Echoes core

A scan of this repository’s Python sources shows **no** `openai.beta.assistants`, `threads`, or `runs` usage in the main product paths. Migration work here is **not** “rewire Assistants API objects.”

**Local** dataclasses such as `Message` and `ConversationHistory` in [`app/agents/models.py`](../app/agents/models.py) are **application models**, not the deprecated OpenAI Assistants API.

## API surfaces in use

Echoes uses **Chat Completions** and **Responses API** side by side depending on path:

### Responses API (`client.responses.create`)

| Location | Notes |
|----------|-------|
| [`assistant_v2_core.py`](../assistant_v2_core.py) | Multiple branches (non-streaming / tool flows) |
| [`scripts/api_call.py`](../scripts/api_call.py) | Example / harness |
| [`scripts/test_raw_responses.py`](../scripts/test_raw_responses.py) | Smoke tests |

### Chat Completions (`client.chat.completions.create`)

| Location | Notes |
|----------|-------|
| [`assistant_v2_core.py`](../assistant_v2_core.py) | Fallback / alternate branches alongside `responses.create` |
| [`app/agents/agent.py`](../app/agents/agent.py) | Async agent loop |
| [`glimpse/sampler_openai.py`](../glimpse/sampler_openai.py), [`glimpse/batch_helpers.py`](../glimpse/batch_helpers.py), [`glimpse/alignment.py`](../glimpse/alignment.py) | Glimpse OpenAI paths |
| [`glimpse/openai_wrapper.py`](../glimpse/openai_wrapper.py) | Wrapper delegates to chat completions |
| [`core_modules/directory_analysis_mixin.py`](../core_modules/directory_analysis_mixin.py) | Analysis helper |
| Various [`scripts/`](../scripts/) | Utilities, benchmarks, demos |
| [`misc/`](../misc/) | Archived / prototype trees (may drift from prod) |

### Tests / mocks

[`tests/test_rate_limiter.py`](../tests/test_rate_limiter.py) and [`tests/test_model_router.py`](../tests/test_model_router.py) mock `chat.completions`; extend mocks when standardizing on Responses API for a given module.

## Recommended hygiene

1. **Per surface, pick a target API**: For [`assistant_v2_core.py`](../assistant_v2_core.py), document when each branch prefers `responses.create` vs `chat.completions.create` (model capability, tools, streaming).
2. **Track deprecations** via OpenAI’s deprecations index whenever upgrading `openai`.
3. **Playground**: Record runs in [`docs/playground/CAPABILITY_MATRIX.md`](playground/CAPABILITY_MATRIX.md) when changing models or agents.
4. **External dependents**: If another repo or hosted workflow still uses Assistants API threads/runs, migrate it using the official Assistants migration guide; Echoes core does not depend on it.

## References (bookmark)

| Topic | URL |
|-------|-----|
| Deprecations | `https://developers.openai.com/api/docs/deprecations` |
| Migrate to Responses | `https://developers.openai.com/api/docs/guides/migrate-to-responses` |
| Assistants migration | `https://developers.openai.com/api/docs/guides/assistants/migration` |
