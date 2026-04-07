# ETHOS

Queryable reference document for `core/ethos.py`.
Sections are tagged for terminal grep access.

```
grep -A 30 "## SCAFFOLD"    ETHOS.md   # what the concept opens with in the codebase
grep -A 30 "## DEFINITION"  ETHOS.md   # global meaning
grep -A 30 "## ETYMOLOGY"   ETHOS.md   # word origin
grep -A 30 "## LOCAL"       ETHOS.md   # what it means right now, under normal circumstances
```

---

## SCAFFOLD

`core/ethos.py` is a 32-line enforcement module. It runs at package import time via
`app/__init__.py` and sets three runtime defaults if they are not already present in
the environment:

| Variable                    | Default   | Meaning                                      |
|-----------------------------|-----------|----------------------------------------------|
| `ECHOES_RESEARCH_ONLY`      | `1`       | Restrict to research mode unless overridden  |
| `ECHOES_EMBEDDINGS_PROVIDER`| `openai`  | Canonical embeddings source                  |
| `ECHOES_PARTNERSHIP`        | `OpenAI`  | Named partner at the root of the runtime     |

The module also holds a tuple `_CANONICAL_PROVIDERS = ("openai",)` and emits a
`logger.warning` if the active provider is not in that set.

The code is entirely declarative policy expressed as imperative Python. Every line
translates 1:1 to an English statement. No computation, no I/O beyond env reads and
writes, no side effects beyond the log warning. The file was created on
**Saturday, March 21, 2026 at 00:33:12** and has not been modified since.

---

## DEFINITION

**ethos** (noun)

1. The distinguishing character, sentiment, moral nature, or guiding beliefs of a
   person, group, or institution.
   — *Merriam-Webster*

2. The characteristic spirit of a culture, era, or community as manifested in its
   attitudes and aspirations.
   — *Oxford English Dictionary*

In ordinary use the word names whatever makes something recognizably *itself* at the
level of values rather than rules. A rule says what to do. An ethos says why and how
the people who wrote the rule think about the world.

---

## ETYMOLOGY

**Greek** — *ēthos* (ἦθος)
- Meaning: habitual character and disposition; moral character; habit; custom; usage.
- Related forms: *ēthikós* (ἠθικός) → English *ethical*.

**Proto-Indo-European root** — `*s(w)e-`
- Third-person reflexive: "one's own."
- Same root as Latin *suus* ("his own"), English *self*, *custom*, *idiom*.
- The PIE sense is: the thing that belongs inherently to a self, not imposed from
  outside.

**First recorded in English**: 1842.

**Aristotle** — *Rhetoric* (Book II, xii–xiv)
- Central to the triad: *ethos* / *pathos* / *logos*.
- Ethos = the credibility and character of the speaker.
- For Aristotle, ethos is not a claimed quality; it is demonstrated through the act
  of speaking itself. You cannot assert your ethos; you can only enact it.

---

## LOCAL

**What "ethos" refers to here, under normal circumstances, when you are hardly paying
attention:**

In 2026, when someone says a project or team "has good ethos," they typically mean
something like: *the vibe is right*, *the values feel consistent*, *it has a spirit
that holds together across decisions*. It is a loose synonym for culture, brand
character, or guiding spirit — used more as a feeling-word than a philosophical term.

In this codebase specifically, the word carries a tighter meaning rooted in its
provenance:

**Historical tribute.** OpenAI is hardcoded as the canonical partner and embeddings
provider not for technical reasons alone but as a marker of origin. The Echoes
project, the Glimpse module, and the early assistant infrastructure were built during
the GPT-4.1 era, using Cursor IDE with OpenAI as the default routing intelligence.
That period — late-night sessions, auto-debugging defaults, cost-versus-intelligence
balance decisions made in real time — is what `ECHOES_PARTNERSHIP = "OpenAI"` names.
The env var is a timestamp in disguise.

**Codex holds override privileges.** The canonical provider is a default, not a lock.
The runtime checks `os.environ.get(...)` first — meaning any caller can override it.
Codex (as the current orchestration layer) retains the right to change the active
provider without modifying the ethos module. That flexibility is deliberate: the
tribute is preserved, but the seat is not bolted down.

**What the file says without saying it:** This project started somewhere specific,
with specific tools, at a specific moment. The ethos module remembers that. Everything
else is allowed to change.
