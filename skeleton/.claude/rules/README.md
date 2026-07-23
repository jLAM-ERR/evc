# .claude/rules/ — OPTIONAL Claude-only adapter

This directory is an **optional refinement for Claude Code only**. The
canonical, portable mechanism for path-scoped rules in this skeleton is
**nested `AGENTS.md` files** (see `example-area/AGENTS.md`) — those work
across Claude Code, Codex, OpenCode, and Kilo Code.

Use `.claude/rules/*.md` with `paths:` glob frontmatter only when you need
glob patterns that directory nesting cannot express (e.g. rules for
`**/*.sql` scattered across the tree):

```markdown
---
paths:
  - "**/*.sql"
---
Rules that load only when matching files are touched.
```

Caveat: path-scoped rules have open bugs in Claude Code (#16299, #16853 on
the watch list) — verify behavior before relying on them. Nothing in the
knowledge loop depends on this directory; deleting it is safe.
