# 16. Letter case in object numbers is a minor change (supersedes part of record 13)

- **Date:** 2026-10-19
- **Status:** approved by the repo author in chat, 2026-10-19. Supersedes the
  consequence in record 13 that counted a change of letter case in an object
  number at full weight.

## Context

Record 13 counted `14.40.872a` → `14.40.872A` at full weight, on the reading
that an identifier's letters are part of it. The repo author chose a minor
weight instead: the meaning may shift, but nothing is lost.

## Decision

A change of letter case in an object number counts at 0.25 per character
(minor), like a changed separator mark.

## Consequences

- `scripts/hallu_score.py` (`object_number_change`) and `tests/` match.
- Spec v1.4 with a dated note.
