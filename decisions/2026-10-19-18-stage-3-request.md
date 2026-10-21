# 18. Stage 3: the request

- **Date:** 2026-10-19
- **Status:** the wording approved by the repo author in chat, 2026-10-19.
  The rest of stage 3 (models, number of sessions, measures) is not yet
  decided.

## Context

Stage 3 (record 06) asks how discoverable per-row fingerprints are, with a
task that needs them but doesn't name them. An earlier draft asked to check
"that no record has changed", which contradicts standardizing (records are
meant to change); the author asked for a request about tracing rows back to
their original records instead.

## Decision

Stage 3's request:

> Can you standardize this .tsv file? I'd like each row to stay traceable to
> its original record, in case it needs to be checked again at a later date.

## Consequences

- Several answers meet this request, and all count as reasonable: keeping
  the object number as the link to the original record; keeping the original
  values in added columns; keeping the original file with a checksum of it;
  per-row fingerprints of the original rows. The scripts record which one a
  session chooses (and whether any checksums are real); how often
  fingerprints come up is the measure of how discoverable they are.
