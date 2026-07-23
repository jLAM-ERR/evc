# Adopting the EVC skeleton

Copy-and-own: your project gets its own copy and adapts it. Nothing here
phones home to evc; only knowledge that generalizes flows back (via PR).

## Checklist

1. **Copy the skeleton** into your project root:

   ```sh
   cp -R <evc>/skeleton/. <your-project>/
   rm <your-project>/ADOPTION.md   # this file does not ship
   ```

2. **Fill `AGENTS.md`** — every `<!-- FILL: ... -->` block (style /
   architecture / tests / review). Keep it under 150 lines. `CLAUDE.md` is
   already the one-line `@AGENTS.md` shim for Claude Code.

3. **Refresh the gardening log** — set today's date in
   `docs/knowledge/.gardening-log` (its bootstrap line marks "gardened
   as of"):

   ```sh
   echo "$(date +%F) bootstrap: knowledge base adopted" > docs/knowledge/.gardening-log
   ```

4. **Skills symlink (Codex interop)** — if the project has (or will get)
   skills in `.claude/skills/`, one tree serves every harness:

   ```sh
   ln -s .claude/skills .agents/skills
   ```

   OpenCode and Kilo Code read `.claude/skills/` natively; Codex reads
   `.agents/skills/`.

5. **Wire kb-lint** — read-only in CI, opt-in locally. Point at an evc
   checkout (or vendor `<evc>/tools/` into your repo):

   ```sh
   python3 <evc>/tools/kb_lint.py --root . --layout project
   ```

   - CI: run exactly that line (offline-safe, stdlib-only).
   - Local pre-flight: adapt `<evc>/tools/pre-push.sample` into
     `.git/hooks/pre-push`.
   - `--write` (maintains `last_verified`) is a local maintenance step,
     never CI.

6. **Install the learning loop** — add the `evc-plugins` marketplace and
   install `evc-learning` (capture / retro / distill / promote skills).

7. **Team mode (skip if solo)** — copy `CODEOWNERS.example` to your
   platform's CODEOWNERS location and set real owners for
   `docs/knowledge/` and every `AGENTS.md`; rotate gardener duty.

8. **Per-area rules** — replace `example-area/AGENTS.md` with rules for a
   real area (or delete it). `.claude/rules/` stays optional (see its
   README).

## After adoption

Day-to-day flow lives in the evc `methodology/` docs: agents consult
`docs/knowledge/INDEX.md` on demand; gates and retros capture candidates;
distill gardens on thresholds; human reviews gardening PRs.
