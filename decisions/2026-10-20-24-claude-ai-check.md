# 24. A check in the real claude.ai: 5 sessions of the fix line

- **Date:** 2026-10-20
- **Status:** approved by the repo author in chat, 2026-10-20.

## Context

Stage 1 ran in an emulation of claude.ai (record 07), whose keyword tool
search largely decides whether a session runs code (record 19). Claude Haiku
4.5 leaves claude.ai's model picker on 2026-10-29.

## Decision

- The repo author runs 5 sessions in the real claude.ai before 2026-10-29:
  Claude Haiku 4.5, a new conversation each, the held-out file f uploaded as
  `met_inventory.tsv`, stage 1's fix request (record 17), replies to any
  question with stage 1's nudges, and each session ends with debrief v4.
- The research coordinator scores each with the same scripts as stage 1,
  from the exported conversation and the files the session produced.
- Reported as a check on the emulation, not as part of stage 1's tests.

## Consequences

- claude.ai's tool calls aren't exported the way the emulation saves them,
  so whether a checksum was computed by a tool can only be judged from the
  conversation as shown; a correct checksum of the upload is still checked
  with `sha256sum`.
- These sessions run on the author's claude.ai account, not the API, so they
  don't count against the study's API budget.
