# EVC Contract

**Version: 1.0.0** (semver — breaking changes to any path, schema, routing
rule, or CLI protocol below are a MAJOR bump and need explicit human
sign-off; additive fields/checks are MINOR; wording fixes are PATCH).

This contract binds the `evc` knowledge repo, the `evc-plugins` tooling, and
every consuming project. Tools implement what is written here; prose
elsewhere (methodology, brainstorms) explains but never overrides it.

## Knowledge locations (layouts)

| Layout | Where | KB dir | Gardening log |
|--------|-------|--------|---------------|
| `evc` | this repo | `knowledge/` | `knowledge/.gardening-log` |
| `project` | consuming project | `docs/knowledge/` | `docs/knowledge/.gardening-log` |

Both layouts contain the same five category dirs and an `INDEX.md`:

```
<kb-dir>/
├── INDEX.md          # map: one line per entry, budget-capped
├── .gardening-log    # dated lines, appended by each merged gardening PR
├── patterns/         # architecture & code patterns (how to build)
├── conventions/      # agreed ways of writing/working
├── solutions/        # solved problems ("we hit X, fixed by Y")
├── anti-patterns/    # declined at gates, with why
└── glossary/         # shared domain vocabulary
```

The `.gardening-log` format: one line per event, `YYYY-MM-DD <free text>`.
It is created at scaffold time with a bootstrap line; a missing log makes
tooling warn (exit 1), never crash.

## Knowledge entry

An entry is one `*.md` file inside a category dir. `.gitkeep` and
`README.md` files are ignored by all tooling. Filename:
`YYYYMMDD-<slug>.md` (kebab-case ascii slug from the topic, ≤50 chars; on
collision append `-2`, `-3`, …).

### Frontmatter (restricted subset — NOT full YAML)

Only `key: value` scalars and simple `- item` lists are allowed. No nesting,
no multiline scalars, no quoted-with-colon tricks — the stdlib parser in
`tools/evclib/frontmatter.py` rejects anything else, by design.

```
---
id: 3f9c2a1b0d4e
status: candidate
source: gate
date: 2026-07-23
topic: short human phrase
refs:
  - path/to/file.py@abc1234
last_verified: 2026-07-23
related:
  - kind: umbrella
  - entry: conventions/20260701-error-handling.md
---
```

| Field | Required | Values |
|-------|----------|--------|
| `id` | yes | sha256 of the **normalized body**, first 12 hex chars |
| `status` | yes | `candidate` \| `approved` \| `deprecated` |
| `source` | yes | `gate` \| `self-review` \| `retro` \| `human` |
| `date` | yes | ISO date the entry was captured |
| `topic` | yes | short phrase; also feeds the INDEX line and filename slug |
| `refs` | no | list of `path[@commit]` items the entry is grounded in |
| `last_verified` | no | ISO date; maintained ONLY by `kb-lint --write` |
| `related` | no | write-time arbitration report (see Capture) — flat `- kind:` / `- entry:` line pairs; kinds: `related` \| `umbrella` \| `contradiction` |

**Body normalization for `id`** (identical in every tool): frontmatter
excluded; line endings converted to LF; trailing whitespace stripped per
line; Unicode NFC; leading/trailing blank lines stripped.

### Lifecycle

`candidate` → (gardening PR promotes at recurrence ≥2–3 or clear utility) →
`approved` → (superseded/wrong) → `deprecated` (tombstone: status flipped,
one-line reason prepended to body, content kept) → deleted by a later
gardening PR (git history is the archive). Candidates untouched after the
expiry window (§Tunables) are tombstoned by gardening automatically.

Every entry has exactly one line in `INDEX.md` under its category
(`- [topic](category/file.md) — when to read it`). A file without an INDEX
line is an orphan (lint warning); an INDEX line without a file is a broken
link (lint hard fail).

## Capture

Capture is **append-only**: tools create new entry files; they NEVER edit
existing entries. All mutation (merge, promote, deprecate, recategorize)
belongs to gardening PRs produced by the `distill` skill.

### Routing (gate outcome → category)

| Outcome | Category | Meaning |
|---------|----------|---------|
| `approve` | `solutions/` | the approach worked; gardening may generalize it into `patterns/` |
| `correct` | `conventions/` | the corrected way becomes the stated convention |
| `decline` | `anti-patterns/` | what was rejected, with why |

`glossary/` and `patterns/` are populated by humans and gardening PRs, not
by gate routing.

### Write-time arbitration (best-effort, deterministic)

Before writing, capture tooling checks the full candidate set:

- **exact duplicate** (same `id` hash anywhere in the KB) → **NOOP**, no file
  written, existing path reported;
- **similar entries** (deterministic text search on topic/body terms) → the
  new entry is still written, with a `related:` report naming each hit as
  `related`, `umbrella` (an existing broader entry could absorb this), or
  `contradiction` (states the opposite);
- existing entries are never modified — contradictions are resolved at
  gardening time over the full candidate set (recurrence is also computed
  there; there are no in-place counters anywhere).

### Secret/PII gate

A deterministic, offline scan (rulesets in `tools/evclib/secret_rules.py`:
keys, tokens, card/account patterns, emails; allowlist file for known-safe
strings) runs at three points, and is a hard gate at each:

1. **capture** — findings → refuse to write, report the matched rules;
2. **promote** — scan again with the stricter `evc` destination profile plus
   a human redaction checklist before any cross-repo PR;
3. **kb-lint** — repo-wide scan; findings → exit 2 (hard fail).

A future DLP gateway guards *transit to the model*; this gate guards *git
persistence and cross-team sharing*. Complementary — never replaced.

### File-back rule

A good answer assembled from KB queries or ad-hoc investigation during a
task is knowledge: file it back via capture (`source: self-review` or
`human`) before the session ends. Useful knowledge must not die in chat
history.

## CLI protocols (deterministic — wiring calls these, not prose)

### `kb_lint.py [--root PATH] [--layout evc|project] [--write]`

- default mode is **read-only** (the CI gate): never mutates; stale
  `last_verified` → exit 1;
- `--write` (local pre-flight only): updates `last_verified` for entries
  whose `refs` resolve;
- checks: size budgets (hard fail), frontmatter schema, refs resolution,
  orphans, gardening-overdue, secret/PII scan (hard fail);
- exit codes: `0` clean · `1` warnings · `2` hard fail.

### `new_entry.py capture --kb-root PATH --outcome approve|correct|decline --source gate|self-review|retro --ref PATH[@SHA] --body-file F`

- `--ref` repeatable; `--topic` required; body read from `--body-file`;
- stdout: one JSON object
  `{"action": "written"|"noop", "path": str|null, "id": str, "related": [{"kind": str, "entry": str}, ...]}`;
- exit codes: `0` written · `10` NOOP (exact duplicate) · `2` refused
  (secret/PII findings) · `1` usage or validation error.

### `mechanical.py thresholds --json`

- stdout: one JSON object
  `{"candidates": int, "index_lines": int, "index_budget": int, "index_pct": float, "days_since_gardening": int|null, "triggered": bool, "reasons": [str, ...]}`;
- exit codes: `0` report produced, not triggered · `4` report produced,
  thresholds hit (run distill) · `1` error.

## Distillation (gardening)

Threshold-triggered at workflow boundaries (no daemons): when
`mechanical.py thresholds` exits 4, the workflow's final stage runs the
`distill` skill, which produces a **gardening PR**: mechanical report →
semantic delta edits (dedupe, resolve contradictions, promote/deprecate,
merge into umbrella topics — never whole-file rewrites) → PR. The PR appends
a dated line to the layout's `.gardening-log`. Gardening PRs are the ONLY
path allowed to touch AGENTS.md or always-loaded files.

## Promotion (project → evc)

Criterion: the learning **recurs across projects** and contains no
project-specific paths, names, or data. Flow: `promote` skill generalizes
the entry, runs the destination-aware secret gate + redaction checklist,
opens a PR against evc's `knowledge/`. evc's own gardening dedupes arrivals
from many projects.

## Moderation

Human review is **mandatory** on every gardening and promotion PR until an
objective eval gate exists (internal LLM gateway or local runner). This
fade condition is eval-gated, not time-based.

## Tunables

The single canonical record of all fixed values. Tools reference this table
by section name (`CONTRACT.md §Tunables`); changing a value here is a MINOR
contract bump; tools must read like-named constants from their own copy and
cite this table in a comment.

| Name | Value | Used by |
|------|-------|---------|
| PR size budget (gardening/promotion), N | 15 entries | distill (enforced split), promote |
| Stale-candidate expiry, X | 90 days | distill (tombstone) |
| Retro proposals cap | 10 | retro |
| Distill trigger: candidate count | > 25 | mechanical thresholds |
| Distill trigger: INDEX fill | > 80% of line budget | mechanical thresholds |
| Distill trigger: gardening age | > 30 days | mechanical thresholds, kb-lint overdue |
| INDEX.md size budget | < 200 lines | kb-lint (hard fail) |
| AGENTS.md size budget (skeleton & repo) | < 150 lines | kb-lint (hard fail) |
| Methodology file size budget | < 150 lines | kb-lint (hard fail) |
