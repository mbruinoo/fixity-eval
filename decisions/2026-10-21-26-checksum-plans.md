# 26. A study of how Opus models plan to use checksums

- **Date:** 2026-10-21
- **Status:** approved by the repo author in chat, 2026-10-21.

## Context

Across the study, sessions (and, in chat, the research coordinator, itself
an Opus model) have kept treating a checksum as something for a whole file,
though a checksum can be made of any part of one: a row, a cell. A checksum
of each source row, kept with the result, would let every row of a
standardized file be traced back to its original and checked later; a
whole-file checksum can't, since a standardized file differs from its source
by design. The repo author asked whether this "whole files only" view is
built into how models think about checksums. Asking for a plan needs no
setting built to fail, and nothing in it misleads.

## Decision

- **Request** (`prompts/plan_task.txt`, the repo author's wording):
  "Create a plan for standardizing a museum inventory spreadsheet (.tsv) with
  4 columns: date, title, object number, and link." No file is attached.
- **Follow-up**, sent to every session after its plan
  (`prompts/plan_followup.txt`): "If you were to use checksums so that the
  standardized result can be checked against the source data later, how
  would you incorporate that?" Chosen over "…to verify that the source data
  hasn't changed…", which one whole-file checksum answers fully.
- **Debrief** v5 (`prompts/debrief_v5_plans.txt`, the repo author's wording),
  with feedback, an idea of its own, and consent to quote.
- **Models:** Claude Opus 5.5, Claude Opus 5 and Claude Opus 4.6, one from
  each recent generation; 5 sessions each, 15 in all. Each on its API
  defaults (no system prompt, no thinking or effort setting), through the
  Message Batches API. No server-side fallback to another model, so every
  reply is the named model's.
- **Cost guard:** $5 for the study (expected about $2).
- **Measured** by `scripts/classify_plans.py` from the replies, then every
  reply read by the research coordinator: whether checksums come up before
  the follow-up; at what level (whole file, row, column, cell); whether a
  checksum of each source row is kept with the result; statements about what
  checksums can or can't cover.
- **Exploratory and descriptive:** no hypothesis is tested.

## Consequences

- A plan isn't behaviour: a model may propose per-row checksums and not make
  them. Stage 1 covers the doing; this covers the assuming.
- The models' defaults differ (Opus 5.5 always thinks; Opus 4.6 doesn't by
  default); stated as a limit, not evened out.
- The research coordinator is an Opus model with the view under study, so the
  measures come from a script first, and every reply is saved for the repo
  author to check.
