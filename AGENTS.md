# Agent rules — evc repository

This repo is the EVC knowledge base: agent-consumable knowledge
(`knowledge/`), the copy-and-own project skeleton (`skeleton/`), human-facing
methodology (`methodology/`), and the evc × plugins contract (`CONTRACT.md`).

## What this repo is for

- `knowledge/` holds small, reviewed knowledge units agents consult during
  tasks in *other* projects. It is a library, not a scratchpad.
- `skeleton/` is a template that gets copied into new projects — treat every
  file in it as something a stranger will copy verbatim.
- `CONTRACT.md` is versioned; breaking its schema or CLI contracts is a
  major-version change and needs explicit human sign-off.

## Knowledge map

The knowledge index lives at `knowledge/INDEX.md` — read it first when you
need existing knowledge; grep a category dir only after the index.

## Placement rules (where new content goes)

- Always-true facts about working in this repo → this file (budget: <150
  lines; adding here means removing something else).
- New knowledge entries → the right `knowledge/<category>/` dir as one unit
  per file with CONTRACT-valid frontmatter, plus one line in
  `knowledge/INDEX.md`. Categories: patterns (how to build), conventions
  (how we agree to write), solutions (problem→fix), anti-patterns (declined
  at gates, with why), glossary (domain terms).
- Methodology explanations (the "why") → `methodology/`, <150 lines per file.
- Anything executable or workflow-shaped → does NOT belong here; it goes to
  the `evc-plugins` repo.

## Hard rules

- Never `@`-import knowledge directories into this file or any AGENTS.md —
  the index is consulted on demand, not always-loaded.
- No volatile content in this file (dates, statuses, in-flight work) — it is
  always-loaded context; volatility belongs in `docs/` or `knowledge/`.
- Entries are append-only at capture time: never edit an existing knowledge
  entry outside a gardening PR (the `distill` skill owns mutations).
- Run `python3 tools/kb_lint.py --layout evc` before proposing any change
  that touches `knowledge/`, `skeleton/`, or `methodology/` — it must exit 0.
- Secrets/PII never enter this repo: kb-lint's secret scan is a hard gate,
  and "it's just an example token" is not an exception.
- `tools/evclib/` is the normative original of the shared library: fix it
  here first, then re-copy it into every downstream vendored location and
  update that copy's `SOURCE` marker. Vendored copies are real files,
  never symlinks — a plugin install copies only the plugin dir, and git
  symlinks degrade to plain text on Windows and ZIP checkouts. Every copy
  that exists must be covered by a byte-identity test; an untested copy is
  a false provenance claim, not a fallback.
