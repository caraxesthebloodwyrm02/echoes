# Incident Report: `submit-pypi` job failure

**Date:** 2026-04-29
**Workflow:** Automatic Dependency Submission (Python) — dynamic workflow
**Job:** `submit-pypi` → step `validate-project`
**Severity:** CI failure (non-blocking to main branch merges, but breaks dependency graph submission)

## Failing Command

```bash
pip-compile --dry-run -o requirements.out requirements.txt
```

## Final Error Excerpt (after partial fix on this branch)

```
ERROR: Cannot install -r requirements.txt (line 20), -r requirements.txt (line 22),
       -r requirements.txt (line 24), langchain-core<1.0.0 and >=0.3.51 and
       langchain==0.3.23 because these package versions have conflicting
       dependencies.

pip._vendor.resolvelib.resolvers.ResolutionImpossible:
  - langchain==0.3.23                  → langchain-core<1.0.0,>=0.3.51
  - langchain_text_splitters-0.3.11    → langchain-core<2.0.0,>=0.3.75
  - langchain_community-0.4.1          → langchain-core<2.0.0,>=1.0.1   ← conflict
  - langchain_community-0.3.27..0.3.31 → langchain<2.0.0,>=0.3.27        ← conflict (vs ==0.3.23)
```

## Root Cause (full analysis)

The `submit-pypi` validation step runs `pip-compile --dry-run` against
`requirements.txt`. Two **independent** but compounding problems made resolution
impossible:

1. **`langchain-core` upper bound (already addressed in earlier commit on this
   branch).** Dependabot PR
   [#200](https://github.com/caraxesthebloodwyrm02/echoes/commit/69286d04)
   bumped `langchain-core` from `>=0.3.45,<2.0.0` to `>=1.3.2,<2.0.0`. This
   crossed the 1.0 boundary while `langchain==0.3.23` still required
   `langchain-core<1.0.0,>=0.3.51`. Reverted in commit
   `e187dd81` to `langchain-core>=0.3.51,<1.0.0`.

2. **`langchain-community` upper bound and `langchain` exact pin (this
   commit).** Even after fixing `langchain-core`, two further conflicts
   prevented resolution:

   - `langchain-community>=0.3.21,<0.5.0` allowed pip-compile to consider
     `0.4.x` releases, all of which require `langchain-core>=1.0.0`. With
     `langchain-core<1.0.0` enforced by `langchain==0.3.23`, the resolver had
     to backtrack to `0.3.x`.
   - But every `langchain-community` release `>=0.3.27` declares
     `langchain<2.0.0,>=0.3.27` as a runtime requirement. The exact pin
     `langchain==0.3.23` is **below** that floor, so the resolver could not
     pick any modern `0.3.x` of `langchain-community` either, eventually
     exhausting all candidates and raising `ResolutionImpossible`.

3. **Loose `langchain` upper bound in `pyproject.toml` optional group.**
   `pyproject.toml [project.optional-dependencies].langchain` had
   `langchain>=0.3.28,<1.3.0`, which would let Dependabot drift the optional
   group across the 1.0 boundary in the future and reproduce the same class of
   conflict (1.x langchain pulls 1.x langchain-core).

4. **`langchain-openai>=1.2.1,<1.3.0`.** This is part of the post-1.0 langchain
   ecosystem and depends on `langchain-core>=1.0.0`, so it also conflicts with
   `langchain==0.3.x`. It is currently used only by the optional `langchain`
   extra (per the inline comment, "Only used by misc/Accounting scripts — not
   imported in production code"). It must move with the rest of the ecosystem.

## Fix Applied (this commit)

Move the entire langchain ecosystem to a self-consistent pre-1.0 set, in both
`requirements.txt` and `pyproject.toml`:

```diff
# requirements.txt
-langchain==0.3.23
-langchain-community>=0.3.21,<0.5.0
-langchain-openai>=1.2.1,<1.3.0
+langchain>=0.3.27,<1.0.0
+langchain-community>=0.3.21,<0.4.0
+langchain-openai>=0.3.0,<0.4.0
 langchain-core>=0.3.51,<1.0.0
 langchain-text-splitters==0.3.11
```

```diff
# pyproject.toml  [project.optional-dependencies].langchain
-    "langchain>=0.3.28,<1.3.0",
-    "langchain-community>=0.3.21,<0.5.0",
-    "langchain-openai>=1.2.1,<1.3.0",
+    "langchain>=0.3.28,<1.0.0",
+    "langchain-community>=0.3.21,<0.4.0",
+    "langchain-openai>=0.3.0,<0.4.0",
     "langchain-core>=0.3.51,<1.0.0",
```

### Local Verification

`pip-compile --dry-run -o /tmp/req.out requirements.txt` now resolves cleanly
with the following ecosystem versions chosen by the resolver:

```
langchain==0.3.28
langchain-community==0.3.31
langchain-core==0.3.84
langchain-openai==0.3.35
langchain-text-splitters==0.3.11
```

This matches the "until langchain-classic migration is done" comment in
`pyproject.toml` and unbreaks the `submit-pypi` validation step.

## Long-term Actions

When the langchain-classic migration is performed, bump the **whole** ecosystem
together (`langchain`, `langchain-core`, `langchain-community`, `langchain-openai`,
`langchain-text-splitters`) to 1.x in a single PR. Until then, the
`langchain-ecosystem` Dependabot group should be prevented from crossing the
1.0 boundary independently. Consider adding to `.github/dependabot.yml`:

```yaml
- package-ecosystem: "pip"
  groups:
    langchain-ecosystem:
      patterns:
        - "langchain*"
  ignore:
    - dependency-name: "langchain-core"
      versions: [">=1.0.0"]
    - dependency-name: "langchain-community"
      versions: [">=0.4.0"]
    - dependency-name: "langchain-openai"
      versions: [">=1.0.0"]
    - dependency-name: "langchain-text-splitters"
      versions: [">=1.0.0"]
```

A complementary improvement would be to make the `submit-pypi` validation a
**required PR check** (rather than a post-merge dynamic workflow) so this class
of conflict is caught before merging future Dependabot bumps.
