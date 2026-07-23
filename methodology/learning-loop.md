# Learning loop — how knowledge improves from real usage

The loop: **capture → distill → promote**, with retro feeding capture.
Format and CLI details are normative in `CONTRACT.md`; this explains why.

## Three knowledge layers (who owns what)

1. **Personal** — each vendor's built-in memory (Claude auto-memory, Codex
   Memories). Machine-local, never in PR flow. Not ours to manage.
2. **Project KB** — `docs/knowledge/` in each project. Git-tracked,
   gardened, the buffer where learnings prove themselves.
3. **Shared evc KB** — `knowledge/` in this repo. The promotion target for
   learnings that generalize across projects.

EVC designs layers 2–3; layer 1 is the platforms' job.

## Capture (event-driven, in-session)

Entry points: workflow **gate decisions** (approve → solution; correct →
convention; decline → anti-pattern), agent **self-review** in auto mode,
**retro** proposals, and the *file-back rule* — a good answer assembled
during a task gets filed, not lost in chat history.

Capture is **append-only**: each learning is a new small file with a
content-hash id. Nothing existing is edited — so parallel sessions and
branches can capture concurrently without losing updates. Arbitration at
write time only *classifies* (duplicate → skipped; similar → marked
`related`/`umbrella`/`contradiction` for the gardener). A deterministic
secret/PII scan refuses to write anything sensitive.

## Retro (session retrospective)

Shaped by the strongest empirical results in the space:

- **Deterministic first**: grep the transcript for cheap signals — explicit
  user corrections are the dominant signal by far.
- **Fresh eyes, in parallel**: analysts with clean context, one per lens
  (errors / successes / corrections), then a single curator merges.
  Re-looping the same context is measurably *worse* than one fresh pass.
- **Principle-level, not instance-level**: "always check X before Y"
  compounds; "file foo.py had a bug" decays.
- ≤10 proposals per retro, each behind explicit approval; retro tracks its
  own acceptance rate and deprioritizes finding types you keep rejecting.

## Distill (gardening — the loop's quality mechanism)

Distillation happens **because size caps force it** (INDEX budget,
candidate-count and staleness thresholds — values in CONTRACT §Tunables).
When thresholds hit, the distill skill produces a **gardening PR**:

- mechanical pass first (deterministic: recurrence, stale refs, budgets),
  semantic judgment second;
- **delta edits only** — whole-file rewrites progressively destroy
  knowledge ("context collapse");
- **never in place** — a branch/PR a human reviews; git history is the
  archive, so deletion is cheap;
- lifecycle: candidate → approved (recurs 2–3× or clearly useful) →
  deprecated tombstone → deleted;
- the only path allowed to touch `AGENTS.md`.

## Promote (project → shared)

When a learning recurs across projects and contains nothing
project-specific, the promote skill generalizes it, re-runs the secret gate
with the stricter shared-KB profile plus a redaction checklist, and opens a
PR against evc. evc's own gardening dedupes arrivals from many projects.

## Consistency without a database

Write-time classification prevents most conflicts; only `approved` entries
are routinely consulted (contradictions among unloaded candidates are
low-harm); gardening + kb-lint catch the rest. Files + git stay the source
of truth because the whole governance model is diff/review/merge — a
vector DB would break that and solve a problem (similarity search) that
isn't contradiction detection anyway.

## Execution model (no daemons, offline CI)

Corporate CI has no LLM access, so CI runs only deterministic checks
(kb-lint). All LLM work happens in dev sessions at workflow boundaries:
thresholds are checked mechanically; when hit, the session runs distill
then and there. Frequency scales with usage, not wall-clock.

Related: `context-model.md` (why budgets exist), `session-hygiene.md`
(where capture naturally happens).
