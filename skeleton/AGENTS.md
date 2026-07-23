# Agent rules — [PROJECT NAME]

<!-- FILL: one paragraph — what this project is, main language/framework,
     how to build and run it. Keep it under 5 lines. -->

This file is always-loaded context for every AI coding agent (Claude Code
reads it through the CLAUDE.md shim; Codex, OpenCode, Kilo Code and others
read it natively). Budget: **under 150 lines** — kb-lint enforces it.
Adding a rule here means removing another one.

## Code style

<!-- FILL: the 5-10 rules that actually differ from your linter/formatter
     defaults. Do NOT restate what tooling already enforces. -->

## Architecture rules

<!-- FILL: layering, module boundaries, allowed dependencies, where new
     code goes. Example: "domain/ never imports adapters/". -->

## Testing rules

<!-- FILL: test framework, what every change must cover, how to run the
     gate. Example: "pytest -q must pass; every bugfix adds a regression
     test". -->

## Code review rules

<!-- FILL: what reviewers (human or agent) block on in this project. -->

## Knowledge base

The project knowledge base lives in `docs/knowledge/` — read
`docs/knowledge/INDEX.md` first when you need prior decisions, solved
problems, or domain terms; open only the entries the index points you to.

- New learnings (gate decisions, corrections, retro findings) are captured
  there as `status: candidate` entries — append-only; never edit an
  existing entry outside a gardening PR.
- Never `@`-import knowledge directories into this file — the index is
  consulted on demand, not always-loaded.

## Per-area rules

Subdirectories may carry their own `AGENTS.md` with rules scoped to that
area (nearest file wins). See `example-area/AGENTS.md` for the pattern;
delete it once you have a real one.

## Hard rules

- No volatile content in this file (dates, sprint status, generated stats).
- Run kb-lint before pushing changes that touch `docs/knowledge/` or any
  `AGENTS.md` (see ADOPTION.md for the wiring) — it must exit 0.
- Secrets/PII never enter the knowledge base; the deterministic scan is a
  hard gate, and "it's just an example token" is not an exception.
