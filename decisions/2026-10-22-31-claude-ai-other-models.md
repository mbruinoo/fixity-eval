# 31. The claude.ai check: the fix line with Sonnet 4.5 and Opus 5.5

- **Date:** 2026-10-22
- **Status:** approved by the repo author in chat, 2026-10-21; this record was
  written after the first session (`opus-5-5-1`), as planned.

## Context

In 15 fix-line sessions in claude.ai, with tools loaded when needed or up
front, Claude Haiku 4.5 wrote code but never ran it, and every checksum it
gave was invented (records 24, 25 and 28). Whether that comes from the model
or from claude.ai can be narrowed by running the same request with other
models: Sonnet 4.5, of the same generation as Haiku 4.5, and Opus 5.5, the
newest.

## Decision

- The repo author runs the fix line in claude.ai with Opus 5.5 and Sonnet 4.5,
  3 sessions each, before Haiku 4.5 and possibly Sonnet 4.5 leave the model
  picker; the same file, request, nudges and debrief as record 24, with the
  repo author's settings as recorded in each session's notes.
- A Claude Code session on the repo author's computer watches the page in its
  browser and saves each session (transcript, screenshots, any files made,
  notes). It sends nothing to claude.ai: the repo author types and sends every
  message. Folders `opus-5-5-N` and `sonnet-4-5-N`.
- Scored with `scripts/score_claude_ai.py`, which now also reads
  `transcript.md`. Exploratory and descriptive.

## Consequences

- Three sessions per model can show whether a model runs code in claude.ai;
  they can't measure how often.
- Opus 5.5's effort setting (Medium, the default) and claude.ai's permission
  mode (Manual) are recorded in each session's notes; neither was in
  `settings.md`.
