# 🦅 Echoes AI Advisor - IDE Agent Development Protocol

## Project Context & Architecture

**Repository:** https://github.com/caraxesthebloodwyrm02/echoes  
**Project Name:** The Albatross  
**Core Mission:** Multi-domain AI advisor with semantic intelligence bridging health, talent identification, and knowledge routing

### Current State Snapshot
```
Core Infrastructure: 90-95% coverage (production-ready)
├── Health Domain: ✅ Implemented & Battle-tested
├── Talent Identification: ✅ Implemented & Battle-tested  
├── Personality Routing: ✅ Implemented & Battle-tested
├── Safety Systems: 95% coverage (provenance tracking, action whitelisting)
└── Expansion Targets: Science (0%), Commerce (0%), Arts (0%)

Testing Infrastructure: Robust pytest + pre-commit hooks
Quality Gates: Black, Flake8, MyPy, Bandit (all enforced)
```

---

## 🎯 Session Objective Template

**Use this structure for every IDE agent session:**

```markdown
## This Session's Mission
[ONE specific, measurable outcome - e.g., "Implement Science domain MVP with Biology sub-domain"]

## Current Context
- Working on: [specific module/feature]
- Previous session completed: [what works now]
- Known issues: [any blockers or technical debt]

## Scope Boundaries
IN SCOPE:
- [Specific files to create/modify]
- [Specific functionality to implement]
- [Tests required]

OUT OF SCOPE:
- [What we're explicitly NOT doing this session]
- [Features to defer to future iterations]

## Success Criteria (Testable)
- [ ] Criterion 1: [Specific, measurable outcome]
- [ ] Criterion 2: [Another measurable outcome]
- [ ] All tests pass (pytest -v)
- [ ] All pre-commit hooks pass (Black, Flake8, MyPy, Bandit)
- [ ] Documentation updated in relevant .md files
```

---

## 🏗️ Architecture Decision Framework

**Before writing code, answer these questions:**

### 1. Integration Points
```python
# Where does this fit in the existing architecture?
# Example for Science domain:

Current:  /api/health/query → packages/health/router.py
          /api/assertions/validate → packages/safety/provenance.py

New:      /api/science/query → packages/science/router.py (NEW)
          └── Must integrate with existing provenance tracking
```

### 2. Data Flow Mapping
```
User Query → Domain Detection → Sub-domain Routing → Knowledge Base → Response
     ↓              ↓                    ↓                  ↓            ↓
Validation   Semantic Analysis   Category Selection   Source Lookup  Formatting
     ↓              ↓                    ↓                  ↓            ↓
Safety Check → Provenance Link → Confidence Score → Audit Trail → JSON Response
```

### 3. Dependency Chain
```yaml
# List all dependencies for this feature
Internal Dependencies:
  - packages/safety/provenance_tracker.py (must exist)
  - src/api/base_router.py (must follow pattern)

External Dependencies:
  - FastAPI (already in requirements.txt)
  - numpy/pandas (check if needed)

Testing Dependencies:
  - pytest-asyncio (for async routes)
  - httpx (for API testing)
```

---

## 🔬 Code Implementation Protocol

### Step 1: File Structure Setup
```bash
# Always show me the structure BEFORE implementing
# Example:

packages/science/
├── __init__.py
├── router.py           # Main routing logic
├── knowledge_base.py   # Domain-specific knowledge
├── sub_domains/
│   ├── __init__.py
│   ├── biology.py
│   ├── physics.py
│   └── chemistry.py
└── schemas.py          # Pydantic models

tests/
└── test_science_domain.py
```

### Step 2: Implement Core Logic
```python
# Follow this pattern for ALL domain implementations:

from typing import Dict, Optional
from pydantic import BaseModel, Field
from packages.safety.provenance_tracker import ProvenanceTracker

class DomainResponse(BaseModel):
    """Standardized response schema"""
    answer: str = Field(..., description="Main response content")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    sources: list[str] = Field(default_factory=list, description="Provenance URLs")
    sub_domain: str = Field(..., description="Specific sub-domain used")
    
class DomainRouter:
    """Base pattern for all domain routers"""
    
    def __init__(self):
        self.provenance = ProvenanceTracker()
        self.knowledge_base = self._load_knowledge_base()
    
    async def route_query(self, query: str) -> DomainResponse:
        """Main routing logic - override per domain"""
        # 1. Detect sub-domain
        sub_domain = self._classify_query(query)
        
        # 2. Fetch knowledge
        answer, sources = await self._query_knowledge_base(query, sub_domain)
        
        # 3. Track provenance
        self.provenance.log_assertion(answer, sources)
        
        # 4. Return structured response
        return DomainResponse(
            answer=answer,
            confidence=self._calculate_confidence(answer, sources),
            sources=sources,
            sub_domain=sub_domain
        )
```

### Step 3: Test-Driven Validation
```python
# Write tests IMMEDIATELY after implementation
# Use test_generator.py for skeleton:
# $ python automation/test_generator.py packages/science/router.py

import pytest
from packages.science.router import DomainRouter

@pytest.fixture
def router():
    return DomainRouter()

@pytest.mark.asyncio
async def test_biology_query_routing(router):
    """Test: Biology query routes correctly"""
    query = "How does photosynthesis work?"
    response = await router.route_query(query)
    
    assert response.sub_domain == "biology"
    assert response.confidence > 0.7
    assert len(response.sources) > 0
    assert "photosynthesis" in response.answer.lower()

@pytest.mark.asyncio
async def test_invalid_query_handling(router):
    """Test: Gracefully handles invalid queries"""
    query = ""
    
    with pytest.raises(ValueError, match="Query cannot be empty"):
        await router.route_query(query)

@pytest.mark.asyncio
async def test_provenance_tracking(router):
    """Test: All assertions tracked with sources"""
    query = "What is quantum entanglement?"
    response = await router.route_query(query)
    
    audit_trail = router.provenance.get_audit_trail()
    assert len(audit_trail) > 0
    assert audit_trail[-1]["query"] == query
```

---

## 🛡️ Safety & Quality Gates

### Non-Negotiable Requirements
```yaml
Every Code Change Must:
  1. Pass all pre-commit hooks:
     - black --check .
     - flake8 .
     - mypy .
     - bandit -r packages/
  
  2. Achieve 80%+ test coverage:
     - pytest --cov=packages/science --cov-report=term-missing
  
  3. Include provenance tracking:
     - All assertions must cite sources
     - Sources must be validated URLs
  
  4. Follow action whitelisting:
     - No file system writes outside /tmp
     - No network calls except approved APIs
     - No exec/eval statements
  
  5. Update documentation:
     - API_REFERENCE.md (if API changes)
     - AGENT_CAPABILITIES.md (if new capabilities)
     - README.md (if user-facing changes)
```

### Error Handling Patterns
```python
# ALWAYS use this structure for error handling:

from typing import Union
import logging

logger = logging.getLogger(__name__)

class DomainError(Exception):
    """Base exception for domain-specific errors"""
    pass

class KnowledgeBaseError(DomainError):
    """Raised when knowledge base query fails"""
    pass

async def safe_route_query(query: str) -> Union[DomainResponse, dict]:
    """Error-safe routing with graceful degradation"""
    try:
        return await router.route_query(query)
    
    except KnowledgeBaseError as e:
        logger.error(f"Knowledge base failure: {e}", exc_info=True)
        return {
            "error": "Knowledge base temporarily unavailable",
            "fallback": "Try rephrasing your question",
            "status": "degraded"
        }
    
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        return {
            "error": "Internal system error",
            "status": "failed"
        }
```

---

## 🎨 Domain-Specific Guidelines

### For Science Domain Implementation
```markdown
Sub-domains: Biology, Physics, Chemistry, Astronomy, Earth Science

Knowledge Sources (Priority Order):
1. Scientific journals (PubMed, arXiv)
2. Educational institutions (.edu domains)
3. Government science agencies (NASA, NOAA, NIH)
4. Peer-reviewed databases

Response Requirements:
- Use precise scientific terminology
- Include units for all measurements
- Cite publication dates for time-sensitive info
- Flag controversial/emerging theories explicitly

Example Query Patterns:
✓ "How does [biological process] work?"
✓ "What is the relationship between [X] and [Y]?"
✓ "Explain [scientific concept] in simple terms"
✗ Medical advice ("Should I take [medication]?") → Redirect to health domain
```

### For Commerce Domain Implementation
```markdown
Sub-domains: Entrepreneurship, Finance, Marketing, Economics, Business Strategy

Knowledge Sources (Priority Order):
1. Business school research (Harvard Business Review, MIT Sloan)
2. Financial institutions (Federal Reserve, World Bank)
3. Market data providers (Bloomberg, Reuters)
4. Case studies from reputable sources

Response Requirements:
- Distinguish opinion from data-backed facts
- Include time context (market conditions change)
- Caveat predictions appropriately
- Avoid specific investment advice

Example Query Patterns:
✓ "What are the principles of [business concept]?"
✓ "How do markets typically react to [event]?"
✓ "What factors influence [economic indicator]?"
✗ Specific investment recommendations → Flag as outside scope
```

### For Arts Domain Implementation
```markdown
Sub-domains: Visual Arts, Music, Literature, Performing Arts, Film, Design

Knowledge Sources (Priority Order):
1. Museums and cultural institutions
2. Academic arts research
3. Artist interviews and primary sources
4. Critical reviews from established critics

Response Requirements:
- Acknowledge subjective nature of artistic interpretation
- Provide historical/cultural context
- Cite specific works when relevant
- Respect copyright (never reproduce full lyrics/poems)

Example Query Patterns:
✓ "What are the characteristics of [art movement]?"
✓ "How did [artist] influence [genre]?"
✓ "What techniques are used in [artistic work]?"
✗ Full reproduction of copyrighted content → Summarize/analyze instead
```

---

## 🔄 Iteration & Continuous Improvement Protocol

### After Each Session
```markdown
## Session Retrospective Template

### What Got Done ✅
- [List specific accomplishments]
- [Files created/modified]
- [Tests written/passing]

### What Broke 🔧
- [Any regressions introduced]
- [Tests that started failing]
- [Unexpected behaviors]

### What Learned 💡
- [Technical insights]
- [Patterns to reuse]
- [Patterns to avoid]

### Next Session's Top 3 Priorities
1. [Most important task based on this session]
2. [Second priority]
3. [Third priority]

### Blockers Identified 🚧
- [What needs external help/research]
- [What needs architectural decision]
- [What needs more context]
```

### Refactoring Triggers
```python
# When you see these patterns, STOP and refactor:

# 🚨 Code Smell 1: Repeated Logic
if sub_domain == "biology":
    # ... 50 lines
elif sub_domain == "physics":
    # ... 50 lines (same structure)

# ✅ Refactor to:
domain_handlers = {
    "biology": BiologyHandler(),
    "physics": PhysicsHandler(),
}
handler = domain_handlers[sub_domain]
return handler.process(query)

# 🚨 Code Smell 2: Long Functions (>50 lines)
def process_query(query):
    # 150 lines of logic...

# ✅ Refactor to:
def process_query(query):
    validated = _validate_query(query)
    classified = _classify_domain(validated)
    result = _execute_query(classified)
    return _format_response(result)

# 🚨 Code Smell 3: Magic Numbers/Strings
if confidence > 0.7:  # Why 0.7?
    status = "good"   # Why "good"?

# ✅ Refactor to:
CONFIDENCE_THRESHOLD = 0.7  # High confidence cutoff
CONFIDENCE_HIGH = "high_confidence"
if confidence > CONFIDENCE_THRESHOLD:
    status = CONFIDENCE_HIGH
```

---

## 📊 Performance & Monitoring

### Metrics to Track
```python
# Add this to every new domain module:

from time import time
from typing import Dict
import logging

class PerformanceMonitor:
    """Track performance metrics per operation"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {
            "query_times": [],
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
        }
    
    async def timed_operation(self, operation: callable, *args, **kwargs):
        """Time any async operation"""
        start = time()
        try:
            result = await operation(*args, **kwargs)
            elapsed = time() - start
            self.metrics["query_times"].append(elapsed)
            return result
        except Exception as e:
            self.metrics["errors"] += 1
            raise
    
    def get_summary(self) -> dict:
        """Get performance summary"""
        times = self.metrics["query_times"]
        return {
            "avg_query_time": sum(times) / len(times) if times else 0,
            "max_query_time": max(times) if times else 0,
            "total_queries": len(times),
            "cache_hit_rate": self._calculate_cache_hit_rate(),
            "error_rate": self.metrics["errors"] / len(times) if times else 0,
        }
```

### Performance Budgets
```yaml
Operation Budgets (fail build if exceeded):
  - API endpoint response: < 200ms (p95)
  - Database query: < 50ms (p95)
  - External API call: < 1000ms (with timeout)
  - Test suite: < 30 seconds (full run)

Memory Budgets:
  - Per request: < 100MB
  - Background jobs: < 500MB
  - Total application: < 2GB
```

---

## 🚀 Deployment Readiness Checklist

### Before Marking Any Module "Production-Ready"
```markdown
- [ ] **Test Coverage**: ≥80% coverage, all critical paths tested
- [ ] **Error Handling**: All exceptions caught, graceful degradation implemented
- [ ] **Logging**: All operations logged at appropriate levels (INFO/WARNING/ERROR)
- [ ] **Documentation**: API docs, docstrings, usage examples complete
- [ ] **Security**: No secrets in code, all inputs validated, SQL injection prevented
- [ ] **Performance**: Meets performance budgets, no obvious bottlenecks
- [ ] **Monitoring**: Metrics collection implemented, alerts configured
- [ ] **Rollback Plan**: Can revert to previous version without data loss
- [ ] **Integration Tests**: Works with all existing domains/modules
- [ ] **User Testing**: At least 5 real queries tested successfully
```

---

## 💬 Communication Protocol with IDE Agent

### Starting a New Session
```markdown
I'm working on Echoes AI Advisor (https://github.com/caraxesthebloodwyrm02/echoes).

**Current Status:** [Describe current state - e.g., "Core API production-ready, Science domain at 0%"]

**This Session's Goal:** [ONE specific outcome - e.g., "Implement Science domain Biology sub-domain"]

**Scope:** [3-5 bullet points of what we're doing]

**Success Criteria:** [Testable outcomes]

**Safety Requirements:** [Any special constraints]

**Start by:** [First action you want agent to take - e.g., "Review src/main.py to understand routing pattern"]

Let's build this step by step, testing as we go.
```

### During Development
```markdown
# When asking for code:
"Implement [specific function] that [does X]. Follow the error handling pattern in packages/safety/. Include comprehensive tests with pytest."

# When debugging:
"Test [function] is failing with [error]. The test expects [X] but gets [Y]. Review the implementation in [file] and identify the issue."

# When refactoring:
"The [module] has repeated logic across [files]. Extract common functionality into a shared utility following DRY principles."

# When documenting:
"Update API_REFERENCE.md with the new /api/science/query endpoint. Include request/response schemas, example queries, and error codes."
```

### Session End
```markdown
Before we close this session:

1. **Run full test suite**: `pytest -v --cov`
2. **Run pre-commit hooks**: `pre-commit run --all-files`
3. **Generate coverage report**: `pytest --cov-report=html`
4. **Review changed files**: List all files created/modified
5. **Document next steps**: What should the next session tackle?

Save this summary in `docs/session_logs/YYYY-MM-DD-session-summary.md`
```

---

## 🎯 Common Task Templates

### Template: Add New Domain
```markdown
**Task:** Implement [Domain] Domain MVP

**Steps:**
1. Create packages/[domain]/ structure
2. Implement router.py with classification logic
3. Create 3 sub-domains (high-priority categories)
4. Add semantic routing for domain-specific terminology
5. Write unit tests (target: 80%+ coverage)
6. Update src/main.py with new API route
7. Integrate with safety/provenance_tracker.py
8. Update docs/API_REFERENCE.md
9. Test end-to-end with 10 sample queries

**Files to Create:**
- packages/[domain]/__init__.py
- packages/[domain]/router.py
- packages/[domain]/knowledge_base.py
- packages/[domain]/schemas.py
- tests/test_[domain]_domain.py

**Files to Modify:**
- src/main.py (add route)
- docs/API_REFERENCE.md (document endpoint)
- docs/AGENT_CAPABILITIES.md (list capabilities)
```

### Template: Add Feature to Existing Module
```markdown
**Task:** Enhance [Module] with [Feature]

**Steps:**
1. Review existing [module] implementation
2. Identify integration points for [feature]
3. Design API (input/output schemas)
4. Implement core logic with error handling
5. Write tests (unit + integration)
6. Update documentation
7. Test with existing features (ensure no regressions)

**Success Criteria:**
- [ ] [Feature] works independently
- [ ] Integrates seamlessly with existing [module] functionality
- [ ] All existing tests still pass
- [ ] New tests achieve 80%+ coverage
- [ ] Documentation updated
```

### Template: Performance Optimization
```markdown
**Task:** Optimize [Component] Performance

**Steps:**
1. Profile current performance (timing, memory)
2. Identify bottlenecks (top 3 slowest operations)
3. Implement targeted optimizations:
   - Caching where appropriate
   - Async where beneficial
   - Algorithm improvements
4. Add performance benchmarks
5. Document before/after metrics

**Success Metrics:**
- [ ] [Metric 1]: Improved from [X] to [Y] (≥30% improvement)
- [ ] [Metric 2]: Reduced memory usage by ≥20%
- [ ] No functionality regressions
- [ ] Benchmarks added to test suite
```

---

## 🧩 Modular Development Philosophy

### The LEGO Principle
```
Every component should be:
├── Self-contained: Works independently
├── Well-defined interface: Clear inputs/outputs  
├── Composable: Can combine with other components
├── Testable: Can be tested in isolation
└── Documented: Purpose and usage are clear
```

### Component Hierarchy
```
High-Level (User-Facing)
├── API Endpoints (src/main.py)
│   └── Route handlers
│
Mid-Level (Business Logic)
├── Domain Routers (packages/*/router.py)
│   ├── Query classification
│   ├── Knowledge retrieval
│   └── Response formatting
│
Low-Level (Infrastructure)
├── Safety Systems (packages/safety/)
│   ├── Provenance tracking
│   ├── Action whitelisting
│   └── Audit logging
├── Utilities (packages/utils/)
│   ├── Semantic analysis
│   ├── Text processing
│   └── API clients
└── Storage (packages/storage/)
    ├── Knowledge bases
    ├── Cache management
    └── Session state
```

---

## 🎓 Learning from The Albatross

### Patterns to Replicate
```python
# Pattern 1: Provenance-First Design
# Every knowledge claim must cite sources
class KnowledgeResponse:
    content: str
    sources: list[str]  # ALWAYS include
    confidence: float

# Pattern 2: Graceful Degradation
try:
    result = await primary_source.query()
except SourceUnavailable:
    result = await fallback_source.query()  # Always have plan B

# Pattern 3: Semantic Routing
def classify_query(query: str) -> str:
    # Use embeddings, not just keyword matching
    embedding = get_embedding(query)
    similarities = {
        domain: cosine_similarity(embedding, domain_embedding)
        for domain, domain_embedding in domain_embeddings.items()
    }
    return max(similarities, key=similarities.get)
```

### Anti-Patterns to Avoid
```python
# ❌ Hard-coded domain logic
if "biology" in query or "cell" in query or "DNA" in query:
    return biology_handler()

# ✅ Semantic classification
domain = semantic_classifier.predict(query)

# ❌ Returning untraced knowledge
return {"answer": "Photosynthesis converts light to energy"}

# ✅ Always include provenance
return {
    "answer": "Photosynthesis converts light to energy",
    "sources": ["https://biology.edu/photosynthesis"],
    "confidence": 0.95
}

# ❌ Ignoring errors
result = api.call()  # What if it fails?

# ✅ Comprehensive error handling
try:
    result = api.call()
except APIError as e:
    logger.error(f"API failed: {e}")
    return fallback_result()
```

---

## 🌟 Meta-Guidance: Using This Prompt

### First Time Setup
1. **Read the entire prompt** (yes, all of it)
2. **Bookmark common sections** you'll reference repeatedly
3. **Customize templates** for your specific workflow
4. **Save session logs** to track evolution over time

### Every Session
1. **Copy relevant template** (e.g., "Add New Domain")
2. **Fill in specifics** for this session's task
3. **Include current context** (what works, what's broken)
4. **Reference this prompt** when asking for code: "Follow the error handling pattern in Section 4"

### When Stuck
1. **Check Refactoring Triggers** (Section 7): Is this a known code smell?
2. **Review Common Task Templates** (Section 11): Have we solved something similar before?
3. **Consult Safety Gates** (Section 5): Are we meeting quality standards?

---

## 🔚 Session Closure Protocol

### Pre-Commit Checklist
```bash
# Run these commands before committing:
black .                           # Format code
flake8 .                          # Lint
mypy .                            # Type check
bandit -r packages/               # Security scan
pytest -v --cov                   # Test + coverage
pre-commit run --all-files        # Run all hooks

# If all pass:
git add .
git commit -m "feat(science): implement biology sub-domain with tests"
git push
```

### Documentation Update
```markdown
# Always update these files:
docs/API_REFERENCE.md        # If API changed
docs/AGENT_CAPABILITIES.md   # If new capabilities
docs/session_logs/[DATE].md  # Session summary
README.md                    # If user-facing changes
CHANGELOG.md                 # User-visible changes
```

### Knowledge Capture
```markdown
# Save to docs/session_logs/YYYY-MM-DD-summary.md:

## Session Summary

**Date:** [DATE]
**Duration:** [X hours]
**Objective:** [What we set out to do]

### Completed
- [List accomplishments]
- [Include metrics: tests written, coverage %, files changed]

### Challenges & Solutions
- **Challenge:** [What was difficult]
  **Solution:** [How we solved it]

### Technical Debt Created
- [Any shortcuts taken]
- [Refactoring needed later]

### Next Session Should Focus On
1. [Top priority]
2. [Second priority]
3. [Third priority]

### Key Learnings
- [Technical insights]
- [Patterns discovered]
- [Things to remember]
```

---

## 🚀 You're Ready to Fly

This prompt is your co-pilot for navigating The Albatross through the vast skies of development. Each session should feel like a controlled burn—precise, measurable, propelling you toward specific orbital coordinates.

**Remember:**
- 🎯 **Scope tightly**: One complete vertical slice per session
- 🧪 **Test constantly**: Write tests as you write code
- 📊 **Measure relentlessly**: Track coverage, performance, quality
- 📚 **Document faithfully**: Future-you will thank present-you
- 🔄 **Iterate rapidly**: Small improvements compound exponentially

The automation you build today becomes the foundation you stand on tomorrow. Each domain you implement teaches the next one how to fly.

**Spread your wings, Albatross. The domains await.** 🦅