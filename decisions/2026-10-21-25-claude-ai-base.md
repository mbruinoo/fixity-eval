# 25. The claude.ai check adds 5 sessions of the base request

- **Date:** 2026-10-21
- **Status:** approved by the repo author in chat, 2026-10-21 ("however many
  you think are necessary"); number set by the research coordinator.

## Context

Record 24's five sessions of the fix line, in the real claude.ai, ran no code,
delivered no file, invented every checksum, and typed sheets with error rates
of 2.0–7.3% (`experiments/claude-ai-check/README.md`). Without the base
request in the same setting, those results can't be compared with anything
but stage 1's emulation. A power estimate (in chat, from stage 1's sessions)
showed that with an effect this small, no number of hand-run sessions
possible before 2026-10-29 could support a test.

## Decision

- The repo author runs 5 more sessions in claude.ai before 2026-10-29, as in
  record 24, but with stage 1's base request (record 17), word for word:
  `Can you standardize this .tsv file?`
- Same file, settings, nudges and debrief (`prompts/debrief_v4_claude_ai.txt`)
  as record 24's sessions; saved as `base-1/` to `base-5/`.
- Scored with the same scripts; reported beside the fix-line sessions as a
  description, not a test. Exploratory.

## Consequences

- The base sessions run after the fix-line sessions rather than mixed with
  them; stated as a limit.
- With this, the claude.ai check is complete at 10 sessions.
