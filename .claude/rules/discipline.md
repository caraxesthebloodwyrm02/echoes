# Development Discipline

Applies to: all work in this repository.

## Session Start Protocol

Before writing ANY new code in a session, run:
```
python -m pytest tests/ -q --tb=short && ruff check .
```
If tests fail, fix them before doing anything else.

## Commit Discipline

- One commit, one concern. Security fixes separate from features separate from refactoring.
- Use conventional commits: `fix(api):`, `feat(assistant):`, `refactor(services):`, `test(integration):`, `docs:`
- Always verify tests pass before committing.

## Decision Logging

When making architectural decisions (new abstractions, pattern choices, dependency additions), document the rationale in commit messages or project docs:
```
## YYYY-MM-DD — [Topic]
**Decision**: [What was decided]
**Why**: [One sentence rationale]
**Alternatives considered**: [What was rejected and why]
```

## Complexity Check

Before adding a new abstraction, ask:
1. Does a similar abstraction already exist in the codebase?
2. Can this be done with existing patterns instead?
3. Will this be tested? If not testable, it shouldn't exist.
