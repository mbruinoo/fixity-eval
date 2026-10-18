# 06. What the confirmatory work tests, in three stages

- **Date:** 2026-10-18
- **Status:** approved by the repo author in chat, 2026-10-18 (the three
  stages and the measures). Stages 2 and 3 get their own records once their
  wording and design are settled.

## Context

SPEC.md asks whether preservation wording improves outputs (§0), and for a
base case with an expected range of error (§1). The exploratory phase's
draft pre-registration (`analysis/preregistration.md`) mainly varied the
setup around the session (file inline or on disk, code tool listed or
searched for, upload guidance on or off), with the wording at two levels, 15
sessions per cell, and the error rate as a secondary measure. The repo
author's plan, written separately, puts the wording first and adds a
question that came up in conversation: whether models treat checksums as
whole-file only, because a file can't contain a correct checksum of itself,
when checksums of smaller pieces (per-row fingerprints) are possible.

## Decision

- **Stage 1** (record 09): confirm on the held-out file that the exploratory
  phase's best line improves on the base request. Confirmatory.
- **Stage 2:** test whether showing that checksums can be made per row helps.
- **Stage 3:** see how discoverable per-row fingerprints are, and how much of
  a roadblock the self-checksum limit is, for Haiku 4.5 and newer models,
  with a task that runs into it (no hint). Framed as "human users can do a
  better job at showing this possibility", not as a test of the models.
  Finding an exact, reproducible quote of the misconception is part of the
  study.
- **Main measures:** SPEC.md's error rate (record 02), and whether a real
  checksum of the uploaded file was produced, computed by a tool in the
  session (`scripts/eval_fixity.py`). Refusals and other no-sheet outcomes are
  reported separately (record 03).
- The draft pre-registration's three setup factors are not part of the
  confirmatory work.

## Consequences

- `analysis/preregistration.md` is rewritten for stage 1 before it's frozen.
- Stage 3 includes models other than Haiku 4.5, which needs a line in SPEC.md
  §2 (with the repo author's permission) and its own record.
