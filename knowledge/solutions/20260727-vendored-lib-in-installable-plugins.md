---
id: 0109662a10c8
status: candidate
source: human
date: 2026-07-27
topic: vendored-lib-in-installable-plugins
refs:
  - tools/evclib
---

Shared libraries used by installable plugins are vendored as real files
inside each plugin directory — never symlinked, never imported from
elsewhere in the repo.

Problem this solves: a Claude Code marketplace install copies ONLY the
plugin's own directory into the user's plugin cache (see any installed
plugin under `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`).
Sibling dirs like `tools/` never arrive, so a relative symlink or an
upward import that leaves the plugin dir dangles on every installed
machine — the plugin works in the repo checkout and crashes everywhere
else. Git symlinks additionally materialize as plain text files on
Windows checkouts and GitHub ZIP downloads.

The EVC instance: `evclib` exists three times. `evc/tools/evclib` is the
only editable original; `evc-plugins/tools/evclib` is the vendoring
waypoint mirroring evc's layout; `evc-plugins/plugins/evc-learning/lib/
evclib` is the installed-shape copy the plugin scripts actually import.
Consistency is enforced, not hoped for: pytest
`test_vendored_lib_byte_identical_to_tools` fails on any byte drift
between the two evc-plugins copies; fixes flow one way only (evc ->
tools -> lib, re-copy both + update the SOURCE marker with the evc
commit); and scripts locate the lib by walking parent dirs trying
`lib/evclib` then `tools/evclib`, so the same code works installed
(lib/ at plugin root) and in a repo checkout (tools/ fallback).
