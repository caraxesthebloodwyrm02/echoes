# Echoes — Plain Brief

Echoes is the audit trail that everything else reads from.

Every time a tool runs anywhere in the Mangrove ecosystem, echoes writes one line
in a logbook: timestamp, what ran, success or failure. It watches and records.
It takes no action of its own.

Think of it as a security camera at the entrance of a building.
It does not decide who gets in. It just keeps the tape.
When you need to know what happened and when, the tape is there.

---

## What reads from it

| Consumer | What it uses |
|----------|-------------|
| personal-rag | Recent tool calls → audit corpus for RAG queries |
| pulse `morning_briefing` | Overnight failures → warnings and priorities |
| pulse `what_should_i_work_on` | Recent failure signals → ranked work queue |

---

## The two layers

**Audit log** — raw record. One line per tool call.
Location: `~/.echoes/audit.ndjson`

**Telemetry** — pattern data over time. Not just "this ran" but
"this fails 20% of the time on Thursdays." The signal above the raw log.

---

## One-line summary

Echoes generates no output of its own.
It makes other systems smarter by giving them history to reason about.
