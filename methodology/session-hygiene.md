# Session hygiene — keeping one session's context clean

Long mixed sessions measurably hurt: multi-turn conversations average a
~39% performance drop vs single-turn, and once a model "takes a wrong
turn" it rarely recovers — restarting fixes it, recapping does not. These
rules turn "restart" into a cheap, routine move.

## One task per session

Start a session for one task; clear between unrelated tasks. The
"kitchen-sink session" is a named anti-pattern. Compaction (`/compact`) is
for *continuations* at natural boundaries, not a substitute for clearing.

## The two-corrections rule

If you've corrected the agent **twice on the same thing**, stop. The
session has degraded context — clear it and restart with a better prompt
(often: write the corrected instruction down first, into the KB or the
task prompt, so the third attempt starts clean and informed).

## Spec, then fresh session

For non-trivial work: write the spec/plan in one session, execute it in a
clean one. The executor reads the spec file — not a degraded conversation
history.

## The handoff pattern

End sessions at task boundaries with a **handoff file**: done / pending /
decisions and why / next step. Build it from ground truth (git diff, test
output), **not** from the model's own recall of the conversation — recall
degrades exactly when the handoff matters most. The next session starts
clean and reads it.

## Externalize state, keep the brain small

- Notes, todos, and intermediate results go to files the agent re-reads —
  not into an ever-growing conversation.
- Keep pointers in context, content on disk ("store bookmarks, not
  books"); anything dropped stays re-fetchable by path.
- Restate the current objective near the end of long sessions (counters
  "lost in the middle" drift).
- Send heavy exploration to subagents that return short conclusions.

## Where the learning loop hooks in

Session end is a capture point: gate outcomes were captured as they
happened; the file-back rule and (periodically) a retro run before the
session closes. See `learning-loop.md`.

Related: `context-model.md` — the same economics, applied to what loads
into every session.
