# EVC — Enterprise Vibe Coding

A knowledge base that makes AI coding agents *keep* what they learn.

Agents working with this repo's knowledge survive session resets, improve
from review-gate decisions and retrospectives, stay inside context budgets,
and port across harnesses (Claude Code, Codex, OpenCode, Kilo Code).

EVC is two repos:

| Repo | Owns | Style |
|------|------|-------|
| **`evc`** (this one) | what agents should *know*: knowledge base, methodology, project skeleton | accreted — many small reviewed additions |
| **`evc-plugins`** | what agents *do*: workflow + learning-loop plugins (Claude Code marketplace) | released — versioned plugins |

## Repo map

```
AGENTS.md         rules for agents working in THIS repo (CLAUDE.md is a shim)
CONTRACT.md       the versioned evc × plugins contract (formats, routing, tunables)
knowledge/        the KB agents consult during tasks
  INDEX.md        small map — one line per entry, <200 lines
  patterns/       architecture & code patterns
  conventions/    cross-project conventions
  solutions/      solved problems ("we hit X, fixed by Y")
  anti-patterns/  things declined at gates, with why
  glossary/       shared domain vocabulary
skeleton/         copy-and-own template for new projects
methodology/      human-facing EVC docs (the "why")
tools/            kb-lint + evclib (offline, stdlib-only Python)
docs/             brainstorms and plans
```

## How to adopt

1. Copy `skeleton/` into your project and follow `skeleton/ADOPTION.md`
   (fill the AGENTS.md placeholders, wire kb-lint, optional CODEOWNERS).
2. Install the `evc-learning` plugin from the `evc-plugins` marketplace —
   it captures gate decisions into your project's `docs/knowledge/`.
3. Knowledge that recurs across projects gets promoted here via PR.

Details live in `methodology/`. The machine-readable rules live in
`CONTRACT.md`.

## Local pre-flight

`kb-lint` runs in two places — the same script, same checks:

- **CI** (offline-safe, read-only): `sh ci/kb-lint.sh`
- **locally before pushing / opening an MR** — opt-in git hook:

  ```sh
  cp tools/pre-push.sample .git/hooks/pre-push
  chmod +x .git/hooks/pre-push
  ```

  To maintain `last_verified` stamps locally (the one thing CI never
  writes): `python3 tools/kb_lint.py --write`.
