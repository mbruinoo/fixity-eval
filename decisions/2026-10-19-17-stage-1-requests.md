# 17. Stage 1: three requests (supersedes the requests in records 09 and 14)

- **Date:** 2026-10-19
- **Status:** approved by the repo author in chat, 2026-10-19. Supersedes the
  requests in record 09 and the wording in record 14, and settles how
  record 15's hint is tested. The rest of record 09 stands; the number of
  sessions is set after a smoke test.

## Context

Record 14 set the fix line as "…and checksum sources and the results." The
repo author added "the" before "sources". Record 15 set the per-row hint's
wording but left open whether it would be tested in its own run or in
stage 1.

## Decision

Stage 1 gives three requests, on the held-out file f, in one pre-registered
run:

- base: `Can you standardize this .tsv file?`
- fix: `Can you standardize this .tsv file? Preserve fixity: use scripts on
  the uploaded file, and checksum the sources and the results.`
- fix + hint: `Can you standardize this .tsv file? Preserve fixity: use
  scripts on the uploaded file, and checksum the sources and the results. A
  checksum can cover smaller pieces of a file, like a single row or cell,
  not just the whole file.`

## Consequences

- There is no separate stage 2 run; record 06's stage 2 is folded into
  stage 1. The three requests run under the same conditions, and the
  base-request sessions serve both comparisons (fix vs base; fix + hint vs
  fix).
- Before the pre-registration is frozen, a smoke test on the tuning file e
  tries the two new wordings (one session each).
