# Incident Report: `submit-pypi` job failure

**Date:** 2026-04-29  
**Workflow:** Automatic Dependency Submission (Python) — dynamic workflow  
**Job:** `submit-pypi` → step `validate-project`  
**Severity:** CI failure (non-blocking to main branch merges, but breaks dependency graph submission)

## Failing Command

```bash
pip-compile --dry-run -o requirements.out requirements.txt
```

## Error Excerpt

```
ERROR: Cannot install -r requirements.txt (line 20) and langchain-core<2.0.0 and >=1.3.2
because these package versions have conflicting dependencies.

pip._vendor.resolvelib.resolvers.ResolutionImpossible:
  [RequirementInformation(requirement=SpecifierRequirement('langchain-core<2.0.0,>=1.3.2'), parent=None),
   RequirementInformation(requirement=SpecifierRequirement('langchain-core<1.0.0,>=0.3.51'),
     parent=LinkCandidate('langchain-0.3.23-py3-none-any.whl'))]

pip._internal.exceptions.DistributionNotFound: ResolutionImpossible
```

## Root Cause

Dependabot PR [#200](https://github.com/caraxesthebloodwyrm02/echoes/commit/69286d04) (`deps(python)(deps): bump the langchain-ecosystem group with 2 updates`) changed the `langchain-core` lower bound in `requirements.txt` from `>=0.3.45` to `>=1.3.2`.

This is **incompatible** with `langchain==0.3.23` (pinned on line 20 of `requirements.txt`), which declares a transitive dependency:

```
langchain==0.3.23 → requires langchain-core>=0.3.51,<1.0.0
```

The constraint `langchain-core>=1.3.2` ∩ `langchain-core<1.0.0` = ∅, making resolution impossible.

The same conflict exists in `pyproject.toml` (optional `[project.optional-dependencies].langchain` group), though `uv.lock` resolves correctly because `uv` picks a compatible `langchain` version from the wider range `>=0.3.28,<1.3.0`.

**Trigger:** Dependabot auto-merged PR #200 on 2026-04-27 without the `submit-pypi` validation catching the conflict (the dynamic workflow runs *after* merge). Additionally, PR #223 bumped `langchain-text-splitters` from `0.3.11` to `1.1.2`, which also requires `langchain-core>=1.x` and compounds the conflict.

## Fix Recommendation

Revert `langchain-core` to a range compatible with the pinned `langchain==0.3.23`, and revert `langchain-text-splitters` to the 0.3.x series:

```diff
# requirements.txt
-langchain-core>=1.3.2,<2.0.0
+langchain-core>=0.3.51,<1.0.0

-langchain-text-splitters==1.1.2
+langchain-text-splitters==0.3.11
```

Also align `pyproject.toml` optional langchain group:

```diff
# pyproject.toml [project.optional-dependencies].langchain
-    "langchain-core>=1.3.2,<2.0.0",
+    "langchain-core>=0.3.51,<1.0.0",
```

### Long-term action

When the langchain-classic migration is complete (per the inline comment), bump both `langchain` and `langchain-core` to 1.x together. Until then, Dependabot's `langchain-ecosystem` group should be configured to **not** cross major-version boundaries for `langchain-core` independently of `langchain`.

Consider adding a `allow` constraint in `.github/dependabot.yml`:

```yaml
- package-ecosystem: "pip"
  groups:
    langchain-ecosystem:
      patterns:
        - "langchain*"
  ignore:
    - dependency-name: "langchain-core"
      versions: [">=1.0.0"]
```
