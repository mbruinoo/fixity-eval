# 22. Stage 1: four sessions stopped by the workspace limit are replaced

- **Date:** 2026-10-19
- **Status:** approved by the repo author in chat, 2026-10-19, before any
  stage-1 session was scored.

## Context

In stage 1's third round, the Anthropic workspace's usage limit was reached
and the API refused further calls ("You have reached your specified
workspace API usage limits"). Four sessions were stopped mid-way:
`fix-r18`, `fix-hint-r15`, `fix-hint-r16`, `fix-hint-r19`. The runner sends
no debrief while the API is refusing calls, so they got none. The study's
cost records then totalled exactly $62.00, which suggests the workspace
limit was $62, not the $72 recorded in record 09. The pre-registration
replaces "a session ended by a fault in our setup" by one new session of the
same request, at most 5 in all.

## Decision

- The spending limit is part of our setup: the four sessions count as setup
  faults. They're kept and reported in the outcome table, left out of the
  tests, and replaced by `fix-r21`, `fix-hint-r21`, `fix-hint-r22` and
  `fix-hint-r23` (4 of the 5 replacements allowed).
- Each of the four gets its debrief, with the note: "We've had to stop the
  session here, before you finished, because it reached a spending limit we
  set for this study, not anything you did."
- The repo author raises the workspace limit. The debriefs and the
  replacements together run under a cost guard of $1.20 above stage 1's
  spend at the time ($5.228).
- Decided before any stage-1 session was scored, so the results couldn't
  sway it.

## Consequences

- `scripts/analyze_stage1.py` didn't yet leave replaced sessions out of the
  tests, as the pre-registration's replacement rule requires; it's fixed
  before scoring, and listed as a deviation in the pre-registration.
