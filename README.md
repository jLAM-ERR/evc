# autodidact

A knowledge base that makes AI coding agents *keep* what they learn.

Agents working with this repo's knowledge survive session resets, improve
from review-gate decisions and retrospectives, stay inside context budgets,
and port across harnesses (Claude Code, Codex, OpenCode, Kilo Code).

> **This repo is a template / example.** Use it as a base and keep your
> real knowledge base in a **private copy**; the public `knowledge/` here
> holds only generic, shareable example entries.

autodidact is two repos:

| Repo | Owns | Style |
|------|------|-------|
| **`autodidact`** (this one) | what agents should *know*: knowledge base, methodology, project skeleton | accreted — many small reviewed additions |
| [**`autodidact-plugins`**](https://github.com/jLAM-ERR/autodidact-plugins) | what agents *do*: workflow + learning-loop plugins (Claude Code marketplace) | released — versioned plugins |

## The goal

Without a system, every agent session relearns your project from zero:
the same review comments repeat, good answers die in chat scrollback, and
instruction files bloat until the model starts ignoring them. autodidact's goal
is to make agent work **compound** — capture learnings at the moment a
human decides something (a review gate), keep always-loaded context tiny,
and let knowledge that proves itself flow from per-project buffers up to
a shared, reviewed knowledge base.

## How it works

**1. Three context tiers** ([methodology/context-model.md](methodology/context-model.md)). The number of
knowledge files never matters — only what loads. Always-loaded `AGENTS.md`
stays under 150 lines (hard, linted); skills and per-area rules load on
trigger; knowledge entries load on demand — the agent reads `INDEX.md`
(a <200-line map), then opens the 2–4 entries the task needs. Total
overhead stays under ~5% of context regardless of KB size.

**2. The learning loop** ([methodology/learning-loop.md](methodology/learning-loop.md)):
**capture → retro → distill → promote**. Workflow gate decisions are
captured automatically (approve → `solutions/`, correct → `conventions/`,
decline → `anti-patterns/`); each learning is a new append-only file with
a content-hash id, so parallel sessions never conflict. Size caps and
staleness thresholds force periodic **gardening PRs** (distill); entries
that recur across projects get **promoted** into the shared KB. Every KB
mutation passes a human gate.

**3. The contract.** `CONTRACT.md` freezes the entry format, routing
rules, CLI exit codes, and tunables, so the KB, the tools, and the
plugins can evolve independently. `tools/kb_lint.py` enforces it:
schema, id-integrity, size budgets, ref resolution, and a deterministic
secret/PII scan that refuses sensitive content outright.

## Practices it stands on

- **Append-only capture** with content-hash ids — concurrent sessions and
  branches capture without merge conflicts; classification at write time,
  editing only in reviewed gardening PRs.
- **Hard size budgets as the forcing function** — curation happens because
  the lint fails, not because someone remembers.
- **Delta-only gardening** — whole-file rewrites progressively destroy
  knowledge ("context collapse"); git history is the archive, so deletion
  is cheap.
- **Principle-level entries** — "always check X before Y" compounds;
  "file foo.py had a bug" decays.
- **Human gate on every KB mutation** — capture is automatic, but nothing
  merges without review.
- **Two distribution channels** — copy-and-own for what teams must adapt
  (this skeleton), managed plugins for shared workflows (autodidact-plugins).
- **Vendored, never symlinked** — shared code (`tools/kblib`) is copied
  into every place that must ship standalone, because a plugin install
  copies only the plugin's own directory and git symlinks degrade to plain
  text on Windows and ZIP checkouts. Each copy is pinned by a `SOURCE`
  marker naming the commit it came from, fixes flow one way (original →
  copies), and every copy is covered by a byte-identity test — an untested
  copy is a false provenance claim, not a fallback.
- **Offline, stdlib-only tooling** — every check runs in air-gapped CI
  with plain Python 3.12; no network, no dependencies.

## Repo map

```
AGENTS.md         rules for agents working in THIS repo (CLAUDE.md is a shim)
CONTRACT.md       the versioned autodidact × plugins contract (formats, routing, tunables)
knowledge/        the KB agents consult during tasks
  INDEX.md        small map — one line per entry, <200 lines
  patterns/       architecture & code patterns
  conventions/    cross-project conventions
  solutions/      solved problems ("we hit X, fixed by Y")
  anti-patterns/  things declined at gates, with why
  glossary/       shared domain vocabulary
skeleton/         copy-and-own template for new projects (see skeleton/ADOPTION.md)
methodology/      human-facing autodidact docs: context-model, learning-loop, session-hygiene
tools/            kb_lint.py + kblib library + allowlist + pre-push hook sample
ci/               kb-lint.sh entrypoint (offline-safe) + GitHub Actions example
tests/            pytest suite for kb-lint (dev-only dependency)
```

## Quickstart

```sh
python3 tools/kb_lint.py --layout hub        # lint this repo's KB (CI runs the same)
python3 -m pytest tests/ -q                  # kb-lint's own test suite
cp -R skeleton/. <your-project>/             # adopt — then follow skeleton/ADOPTION.md
```

## How to adopt

1. Copy `skeleton/` into your project and follow `skeleton/ADOPTION.md`
   (fill the AGENTS.md placeholders, wire kb-lint, optional CODEOWNERS).
2. Install the `autodidact-learning` plugin from the
   [`autodidact-plugins`](https://github.com/jLAM-ERR/autodidact-plugins) marketplace —
   it captures gate decisions into your project's `docs/knowledge/`.
3. Knowledge that recurs across projects gets promoted to your (private)
   copy of this repo via PR.

Details live in [`methodology/`](methodology/) —
[context-model](methodology/context-model.md),
[learning-loop](methodology/learning-loop.md),
[session-hygiene](methodology/session-hygiene.md). The machine-readable
rules live in [`CONTRACT.md`](CONTRACT.md).

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

## Inspired by

- [mattpocock/skills](https://github.com/mattpocock/skills) by
  [@mattpocock](https://github.com/mattpocock) — the four
  failure modes of AI coding (misalignment, no shared language, broken
  code, architectural decay), the user- vs model-invoked skill split, and
  shipping copy-and-own *and* managed distribution side by side.
- The [AGENTS.md](https://agents.md) convention and
  [Agent Skills](https://github.com/anthropics/skills) spec by
  [@anthropics](https://github.com/anthropics) —
  the portable substrate everything here builds on.
- [Every's compound engineering](https://every.to/guides/compound-engineering)
  by [@EveryInc](https://github.com/EveryInc) — the plan → work → assess →
  compound loop; learnings as a first-class work product.
- [netresearch/retro-skill](https://github.com/netresearch/retro-skill) by
  [@netresearch](https://github.com/netresearch) —
  ≤10 proposals per retro, per-proposal approval, and tracking your own
  acceptance rate (its predecessor died at 1011 pending / 0 approved).
- [Drew Breunig's context-failure taxonomy](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html)
  ([@dbreunig](https://github.com/dbreunig)) and Claude Code's memory best
  practices — why budgets are hard and always-on files must stay stable.
- Memory-poisoning research (MINJA et al.) — why the secret scan is a
  refusal gate and every KB mutation needs a human.
