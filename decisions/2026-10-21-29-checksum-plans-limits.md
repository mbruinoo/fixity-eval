# 29. Checksum-plans study: longer reply limits for Opus 5.5 and Opus 5, and a $13 guard

- **Date:** 2026-10-21
- **Status:** approved by the repo author in chat, 2026-10-21. Adds to
  records 26 and 27; supersedes their cost guard.

## Context

In the smoke test (`experiments/smoke-2026-10-21-checksum-plans/`), Opus 5.5,
on its default effort, spent the whole 16,000-token limit thinking and
returned no text, twice; Opus 5 was cut off in its script and its debrief.
Opus 4.6 and Haiku 4.5 finished well within the limits. The smoke test cost
$1.10 for four sessions.

## Decision

- Reply limits for Opus 5.5 and Opus 5: 64,000 tokens for the script and the
  follow-up, 16,000 for the debrief. Opus 4.6 and Haiku 4.5 keep 16,000 and
  4,000. The models' own settings are unchanged (no effort or thinking
  setting).
- First, one Opus 5.5 session with the new limits
  (`experiments/smoke-2026-10-21-checksum-plans-opus55/`, cost guard $1.50).
  If its script and follow-up answers both come back with text, the full run
  of 20 sessions starts; if not, it stops and the research coordinator
  reports.
- Cost guard for the full run: $13 (expected $7–8; the guard checks each
  round's worst case before sending it).

## Consequences

- Study spend could reach about $79 of $100.
- Neither check session is counted in the results.
