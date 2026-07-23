# Project knowledge base (the learning loop)

This directory is where your project's AI-agent knowledge accumulates and
improves. Format and rules: `CONTRACT.md` in the evc repo (normative).

How knowledge flows:

1. **capture** — workflow gate decisions (approve / correct / decline),
   agent self-review findings, and retro proposals land here as small
   `status: candidate` entries, one per file, append-only.
2. **distill** — when thresholds hit (too many candidates, index near its
   budget, gardening overdue), the distill skill produces a gardening PR:
   merge duplicates, resolve contradictions, promote good candidates to
   `approved`, tombstone stale ones. A human reviews and merges.
3. **promote** — learnings that recur across projects and contain nothing
   project-specific get PR'd upstream to the shared evc knowledge base.

Ground rules:

- `INDEX.md` is the map — one line per entry; agents read it first.
- Entries are never edited outside a gardening PR (append-only capture).
- kb-lint guards this dir in CI and pre-push: budgets, schema, stale refs,
  orphans, secret/PII scan.
- `.gardening-log` records gardening runs — do not delete it.
