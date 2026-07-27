# EVC Contract

**Version: 1.1.0** (semver — breaking changes to any path, schema, routing
rule, or CLI protocol below are a MAJOR bump and need explicit human
sign-off; additive fields/checks are MINOR; wording fixes are PATCH).

History — each release is an annotated git tag `vX.Y.Z` in this repo:

- **1.1.0** — `capture --source` accepts `human` (additive).
- **1.0.0** — initial contract.

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

**Grammar (normative — parsers implement exactly this):**

- The file MUST start with a line that is exactly `---`; frontmatter is every
  line until the next line that is exactly `---`; the body is everything
  after that line.
- Each frontmatter line is exactly one of:
  - scalar: `^([a-z_]+): (.+)$` — key, colon-space, non-empty value (the
    value is the rest of the line, trailing whitespace stripped; it MAY
    contain further colons);
  - list head: `^([a-z_]+):$` — MUST be followed by ≥1 item lines;
  - list item: `^  - (.+)$` — exactly two spaces, dash, space, non-empty
    scalar item (may contain colons).
- Rejected (parse error → schema hard fail): blank lines inside frontmatter,
  `#` comments, duplicate keys, keys not matching `[a-z_]+`, empty values,
  list heads with zero items, item lines not preceded by a list head, any
  indentation other than the two forms above, tabs, unknown keys (v1 keys
  are exactly the table below; new keys are a MINOR contract bump).

Accepted example: the block below. Rejected examples: `topic:` with no
items; `Topic: x` (uppercase); `refs: [a, b]` (flow list); `note: >` /
multiline; `  extra: nested` (nesting); a second `id:` line (duplicate).

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
  - umbrella:conventions/20260701-error-handling.md
---
```

| Field | Required | Values |
|-------|----------|--------|
| `id` | yes | sha256 of the **normalized body**, first 12 hex chars |
| `status` | yes | `candidate` \| `approved` \| `deprecated` |
| `source` | yes | `gate` \| `self-review` \| `retro` \| `human` |
| `date` | yes | ISO date the entry was captured |
| `topic` | yes | short phrase; also feeds the INDEX line and filename slug |
| `refs` | no | list of `path[@commit]` items the entry is grounded in (grammar below) |
| `last_verified` | no | ISO date; maintained ONLY by `kb-lint --write` |
| `related` | no | write-time arbitration report (see Capture) — list of `<kind>:<category/file.md>` scalars; kinds: `related` \| `umbrella` \| `contradiction` |

**Body normalization for `id`** (identical in every tool): frontmatter
excluded; line endings converted to LF; trailing whitespace stripped per
line; Unicode NFC; leading/trailing blank lines stripped.

**`refs` grammar and resolution (normative):**

- Item form: `path` or `path@commit`. Split on the **last** `@`; `commit`
  must match `[0-9a-f]{7,40}` — if the trailing segment doesn't match, the
  whole item is a plain path containing `@`.
- `path` is relative to the **repo root** (kb-lint's `--root`), forward
  slashes, no leading `./`, no `..` segments (schema fail).
- **Resolution (v1)**: the path (after stripping `@commit`) exists in the
  working tree AND its fully-resolved location stays inside the repo root —
  a path that escapes the root through a symlink is a hard fail, like a
  malformed ref. The commit hash is provenance metadata, NOT verified in v1
  (verifying historical trees needs git and is a possible MINOR addition).
- Severity table:

| Condition | Read-only mode | `--write` mode |
|-----------|----------------|----------------|
| no `refs` key | ok, `last_verified` ignored | ok, never touched |
| all refs resolve | ok (regardless of `last_verified` age/absence) | set `last_verified` to today (add or update) |
| ≥1 ref fails to resolve | warning → exit 1 ("stale entry") | warning → exit 1; `last_verified` NOT updated |
| malformed ref item | schema hard fail → exit 2 | same |

Staleness in v1 is purely refs-resolution failure — `last_verified` age is
informational and never triggers exit codes.

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

**Anti-sprawl order, reconciled (normative).** The design preference
"patch existing entry → extend umbrella topic → only then new entry" is
split by phase, because append-only wins at capture (concurrency safety):

- **at capture**: the order is *classification only* — arbitration marks the
  new candidate `umbrella:<entry>` (should be absorbed) or
  `related:<entry>`; the file is still written, nothing is edited;
- **at distill (gardening PR)**: the order is *edit actions* — first fold
  candidates into the existing entry they patch, then into their umbrella
  topic, and only keep them standalone when neither applies.

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

A deterministic, offline scan runs at three points, and is a hard gate at
each:

1. **capture** — findings → refuse to write, report the matched rule IDs;
2. **promote** — scan again with the stricter `evc` destination profile plus
   a human redaction checklist before any cross-repo PR;
3. **kb-lint** — scans **every regular file under the KB dir** (entries,
   INDEX, READMEs, `.gardening-log`, anything else) except the local
   allowlist file; findings → exit 2 (hard fail); a file that is not valid
   UTF-8 is reported as a warning ("unscannable"), never silently skipped.

**Normative ruleset.** `tools/evclib/secret_rules.py` in this repo is the
normative implementation, versioned with this contract; vendored copies must
be byte-identical to their `SOURCE`-marked evc commit. Fixed rule IDs (v1 —
removing or renaming one is MAJOR; adding is MINOR):

| ID | Detects |
|----|---------|
| EVC-SEC-001 | private key blocks (`-----BEGIN … PRIVATE KEY-----`) |
| EVC-SEC-002 | AWS access key IDs (`AKIA…`/`ASIA…`-style) |
| EVC-SEC-003 | assigned credentials (`api_key/token/secret/password = <literal>`) |
| EVC-SEC-004 | bearer tokens / JWTs (`eyJ…` triplets, `Bearer <token>`) |
| EVC-SEC-005 | payment card numbers (13–19 digits, Luhn-valid) |
| EVC-SEC-006 | IBAN-shaped account numbers |
| EVC-PII-001 | email addresses |

**Allowlist semantics**: a plain-text file (one literal string per line,
`#` comments allowed); a finding is suppressed iff its exact matched text is
an allowlist line. Profiles: `project` uses the project's local allowlist;
the `evc` destination profile (promote, evc's own kb-lint) uses ONLY evc's
`tools/allowlist.txt` — a project's allowlist never travels upstream.
Locations: `evc` layout/profile → `<root>/tools/allowlist.txt`; `project`
layout → `<kb-root>/.secret-allowlist`. A missing allowlist file means an
empty allowlist.

A future DLP gateway guards *transit to the model*; this gate guards *git
persistence and cross-team sharing*. Complementary — never replaced.

### File-back rule

A good answer assembled from KB queries or ad-hoc investigation during a
task is knowledge: file it back via capture (`source: self-review` or
`human`) before the session ends. Useful knowledge must not die in chat
history.

## CLI protocols (deterministic — wiring calls these, not prose)

Root conventions: `kb-lint` takes the **repo root** plus a layout (it also
checks files outside the KB dir); capture and thresholds take `--kb-root` =
the **KB dir itself**. Mapping: layout `evc` → kb-root `<root>/knowledge`;
layout `project` → kb-root `<root>/docs/knowledge`. The gardening log is
`<kb-root>/.gardening-log` in both layouts.

### `kb_lint.py [--root PATH] [--layout evc|project] [--write]`

- default mode is **read-only** (the CI gate): never mutates; stale
  `last_verified` → exit 1;
- `--write` (local pre-flight only): updates `last_verified` for entries
  whose `refs` resolve;
- checks: size budgets (hard fail), frontmatter schema, refs resolution,
  orphans, gardening-overdue, secret/PII scan (hard fail);
- exit codes: `0` clean · `1` warnings · `2` hard fail.

### `new_entry.py capture --kb-root PATH --topic TOPIC --outcome approve|correct|decline --source gate|self-review|retro|human --ref PATH[@SHA] --body-file F`

- `--ref` repeatable (optional); `--topic` required; body read from
  `--body-file`;
- stdout carries one JSON object on exits 0, 10, and 2:
  `{"action": "written"|"noop"|"refused", "path": str|null, "id": str, "related": [{"kind": str, "entry": str}, ...], "findings": [str, ...]}`
  (`findings` = matched secret rule IDs, empty unless refused; `path` = the
  written file, or the existing duplicate on noop, or null on refused);
- exit `1` (usage/validation error): no stdout JSON, diagnostic on stderr;
- exit codes: `0` written · `10` NOOP (exact duplicate) · `2` refused
  (secret/PII findings) · `1` usage or validation error.

### `mechanical.py thresholds --kb-root PATH --json`

- `--kb-root` required — the KB dir to inspect (see mapping above); a
  missing or KB-shapeless dir (no `INDEX.md`) → exit 1, diagnostic on
  stderr;
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
