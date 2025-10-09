# API Reference

> Auto-generated from FastAPI routes.

## Endpoints

### `GET /openapi.json`

No description

---

### `GET /docs`

No description

---

### `GET /docs/oauth2-redirect`

No description

---

### `GET /redoc`

No description

---

### `POST /api/assertions/validate`

Validate that an assertion includes proper provenance.

---

### `POST /api/hil/feedback`

Capture human-in-the-loop feedback for model improvement.

---

### `GET /api/hil/feedback`

Retrieve queued feedback for review.

---

### `POST /api/agent/execute`

Execute agent action with safety controls.

---

### `POST /api/agent/kill`

Emergency kill-switch for runaway agents.

---

### `GET /api/agent/status/{agent_id}`

Get status of a running agent.

---

### `GET /api/health`

System health check.

---

### `GET /api/metrics`

System metrics and KPIs.

---

### `POST /api/auth/login`

Authenticate user and return JWT access token.

---

### `POST /api/auth/logout`

Logout current user.

---

### `GET /api/auth/me`

Get current authenticated user profile.

---

### `GET /api/auth/verify`

Verify if the provided token is valid.

---

### `POST /api/science/biomedical/search`

Search biomedical literature with provenance tracking.

---

### `POST /api/science/chemistry/simulate`

Simulate chemical reactions with safety checks.

---

### `POST /api/science/physics/simulate`

Simulate physics problems for space travel, materials science, etc.

---

### `POST /api/commerce/ubi/simulate`

Simulate Universal Basic Income economic impact.

---

### `POST /api/commerce/employment/match`

Match job seekers with employment opportunities using AI.

---

### `POST /api/commerce/economy/forecast`

Forecast economic indicators and market trends.

---

### `POST /api/arts/create`

Generate creative works with ethical controls.

---

### `POST /api/arts/analyze/cultural`

Analyze content for cultural context and sensitivity.

---

### `POST /api/arts/language/preserve`

Analyze and preserve endangered languages.

---

### `POST /api/arts/history/analyze`

Analyze historical trends and their modern implications.

---

### `POST /api/arts/harmonyhub/emotional-message`

Create music-based emotional communication message.

---

### `POST /api/arts/harmonyhub/therapeutic-session`

Start AI-powered therapeutic music session.

---

### `POST /api/arts/harmonyhub/personalized-feed`

Create personalized emotional content feed.

---

### `GET /api/arts/harmonyhub/market-intelligence/{symbol}`

Get market intelligence for creative assets and artists.

---

### `GET /api/arts/harmonyhub/status`

Get HarmonyHub integration status and capabilities.

---

### `POST /api/finance/personal/analyze`

Comprehensive personal finance analysis.

---

### `POST /api/finance/enterprise/analyze`

Comprehensive enterprise finance analysis.

---

### `POST /api/finance/insights/quick`

Get quick financial insights and suggestions.

---

### `POST /api/finance/goals/analyze`

Analyze and structure financial goals.

---

### `POST /api/finance/prediction/income`

Predict future income growth.

---

### `POST /api/finance/prediction/retirement`

Project retirement fund growth.

---

### `POST /api/finance/portfolio/optimize`

Optimize investment portfolio allocation.

---

### `POST /api/finance/scenario/investment`

Simulate different investment scenarios.

---

### `GET /api/finance/health`

Health check endpoint for FinanceAdvisor module

---

### `GET /`

Root endpoint with API information.

---
