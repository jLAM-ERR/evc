# Context model — why the KB can grow but context cannot

An LLM agent has a fixed-size working memory (its *context window*). Every
line that is always loaded competes with the actual task. Research is
unambiguous: models degrade as context grows, and bloated instruction files
don't just cost tokens — the model starts *ignoring* instructions.

The EVC answer: the number of knowledge files doesn't matter; **only what
loads matters**. Three tiers:

## Tier 1 — always loaded (the only real cost)

The `AGENTS.md` chain (plus the `CLAUDE.md` shim for Claude Code). Budget:
**under 150 lines** per file, enforced by kb-lint. ~200 lines is roughly 2K
tokens ≈ 1% of a typical window — kept small on purpose.

Rules for Tier 1 content:

- Per-line test: *"would removing this line cause mistakes? If not, cut."*
- No volatile content (dates, sprint status, generated stats) — always-on
  files are part of the cached prompt prefix; stability makes them ~10×
  cheaper and keeps behavior consistent.
- Pointers, not prose: `AGENTS.md` carries one line pointing to
  `knowledge/INDEX.md`; it never inlines knowledge.

## Tier 2 — loaded by trigger

- Skills: only the name + description (~25–50 tokens each) are preloaded;
  the body loads on invocation.
- Per-area rules: nested `AGENTS.md` files load when the agent works in
  that area (portable across harnesses). `.claude/rules/` globs are an
  optional Claude-only refinement.

## Tier 3 — on demand, one small unit at a time

"One knowledge unit per file" is a *context* rule, not a filing preference:
the agent reads `INDEX.md` (a map, <200 lines), then opens the 2–4 entries
the task needs (~30 lines each). Typical overhead: 1–2K tokens — **under 5%
of context regardless of KB size**.

Supporting mechanisms:

- **Subagents for heavy reading**: workers burn their own context exploring
  and return short conclusions to the main session.
- **Distillation** (see `learning-loop.md`) keeps INDEX and entries inside
  their budgets — the caps are what force curation to happen.

## Forbidden

- `@`-importing knowledge directories into any always-loaded file — it
  turns Tier 3 into Tier 1 and defeats the whole model.
- Growing a budgeted file "temporarily". Budgets are hard; kb-lint fails
  the build.

Related: `session-hygiene.md` (keeping one session's context clean),
`learning-loop.md` (how knowledge gets in and stays small).
