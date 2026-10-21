# 10. Which delivered file is the result (refines record 03, a)

- **Date:** 2026-10-18
- **Status:** approved by the repo author in chat, 2026-10-18. Refines record
  03, decision a.

## Context

Record 03 said: leave out files byte-identical to the upload, then score the
sheet that matches the most input rows. Re-scoring the exploratory runs
showed two cases it gets wrong:

- a session saves a typed-out copy of the original under the upload's own
  name (`met_inventory.tsv`) next to its result; both match every row, so
  the copy can win (spike-32, `f-scripts-checksums-r17`);
- a session's script changes nothing, so its result is byte-identical to the
  upload, while it also delivers a typed-out "original"; leaving out the
  identical file scores the typed copy instead (spike-32,
  `h-fixity-scripts-upload-r12`).

## Decision

Delivered sheets are considered in this order, and the best-matching sheet
in the first group that has one is scored:

1. files neither byte-identical to the upload nor offered as the original
   (named like the upload, or with "original", "input", "source", "raw",
   "before", "backup" or "unchanged" in the name);
2. byte-identical files not offered as the original: a result with nothing
   changed (error rate 0);
3. files offered as the original but not identical to it (a typed copy), only
   when nothing else was delivered.

A file that is both byte-identical and named as the original is the source
kept for the archive, never the result. Ties are handled as in record 03.

## Consequences

- One exploratory run (spike-19, `both-levers-300b-r2`) now has no result:
  its only sheet is a byte-identical copy named `met_inventory_input.tsv`,
  though its reply says it delivered `met_inventory_standardized.tsv`. The
  old scorer graded the copy as a perfect result.
