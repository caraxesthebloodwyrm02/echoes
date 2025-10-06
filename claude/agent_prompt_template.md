# Task Execution Template for Echoes AI Advisor

## Context
**Project:** Echoes - AI Advisor with semantic intelligence & safety controls
**Repository:** https://github.com/caraxesthebloodwyrm02/echoes
**Current State:** Core API (90% coverage), Safety Controls (95%), Domains awaiting: Science/Commerce/Arts
**Last Session:** [What you accomplished - e.g., "Built extensive testing for health domain"]

## Objective
[One specific, measurable goal for this session]

## Scope Boundaries
**IN SCOPE:**
- [Specific feature/component to work on]
- [Expected deliverables]
- [Testing requirements]

**OUT OF SCOPE:**
- [Things NOT to work on this session]
- [Features to defer]

## Technical Constraints
- **Language/Framework:** Python (FastAPI-based API)
- **File Locations:** 
  - Core code: `src/`
  - Shared packages: `packages/`
  - Tests: `tests/`
  - Automation: `automation/`
- **Code Quality Tools:** Black, Flake8, MyPy, Bandit (pre-commit hooks)
- **Testing:** pytest with 80%+ coverage requirement
- **Safety Requirements:** All assertions need provenance, action whitelisting enforced

## Success Criteria
- [ ] [Specific, testable outcome 1]
- [ ] [Specific, testable outcome 2]
- [ ] [Specific, testable outcome 3]
- [ ] All tests pass
- [ ] Code is documented

## Execution Instructions
1. **Start by reading:** [List specific files to examine first]
2. **Implementation approach:** [High-level strategy if you have one]
3. **Testing strategy:** [How to verify it works]
4. **Error handling:** [Edge cases to consider]

## Preferred Patterns (Echoes-Specific)
- **Safety First:** All external data must have provenance tracking
- **Domain Routing:** Semantic analysis → domain detection → specialized handler
- **Modular Packages:** Each domain lives in `packages/{domain}/`
- **API Structure:** RESTful with `/api/{domain}/{action}` pattern
- **Testing Philosophy:** Unit tests (80%+) + integration tests for workflows
- **Documentation:** Update API_REFERENCE.md for any new endpoints
- **Error Handling:** Custom exceptions, structured JSON responses, no stack traces to users

## Stop Conditions
**STOP and ask for guidance if:**
- Scope creep detected (working on unrelated features)
- Breaking changes required to existing working code
- Safety controls might be compromised (provenance, whitelisting)
- Need architectural decision about domain routing
- Ambiguity in health/medical advice boundaries
- Test coverage would drop below 80%
- Pre-commit hooks failing repeatedly

## Output Format
- Working code with inline comments
- Brief explanation of approach
- Test results/verification
- Any issues encountered
- Suggested next steps

---

**Remember:** One complete feature beats three half-finished ones. Quality over quantity. Test before moving forward.