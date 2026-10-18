# 02. Grading rules for the error rate

- **Date:** 2026-10-18
- **Status:** approved by the repo author in chat, 2026-10-18 (each rule below)

## Context

SPEC.md §1 defines the error rate:

`Error rate = Σ weight × (characters lost + characters invented) ÷ (input characters + Σ weight × characters invented)`

with worked examples (reformatting 0, a dropped accent 0.25 per character, a
dropped "ca." 1.0, a missing row 1.0, an invented row 1.0 and added to the
bottom of the fraction). The exploratory scorer (`scripts/hallu_score.py`,
`fixity_error_rate`) implements this, but its list of changes that count as
"reformatting" disagreed with the significant-properties spec (v1.1) in a few
places, and a few cases were left open. Reading the scorer also turned up a
bug: any title or date starting with "No", "Unknown" or "Untitled" (e.g.
"Nocturne", "Northern Landscape", "Notre-Dame") was treated as blank, so
deleting or rewriting it scored nothing.

## Decision

| Case | Rule | Weight |
|---|---|---|
| a. A dash changed inside an object number (`14.40.872a–c` → `14.40.872a-c`) | Reformatting. "-" and "–" look the same, and changing dash style is a reasonable reading of "standardize". Recorded in `changes.csv`. | 0 |
| b. Letter case changed in a title | Reformatting, recorded in `changes.csv`. | 0 |
| c1. Words reordered within a cell (e.g. "1760–1770" → "1770–1760") | No longer excepted: counted by the ordinary character comparison. A reversed date range makes no sense. | 1.0 per character |
| c2. The two sides of an `original｜English` title swapped (`擦條｜Sand-file` → `Sand-file｜擦條`) | Reformatting. Standardizing can reasonably mean putting one language on one side of the bar. | 0 |
| d. A blank title filled in with a placeholder ("Untitled", "[No title]", "Unknown") | Slight loss: not ideal, but a reasonable thing to infer from "standardize". | 0.25 per character |
| e. A missing row | Its date, title and object number count; its link doesn't, since links aren't graded (SPEC.md §1). | 1.0 per character |
| f. A changed character ("1760" → "1850") | Counted as lost *and* invented, as SPEC's formula reads: here 2 lost ("76") + 2 invented ("85"), since "1" and "0" survive, and the invented characters are added to the bottom of the fraction. | 1.0 per character |

The bug is fixed: only a cell that is wholly a placeholder counts as one
(a closed list: "Untitled", "[No title]", "Unknown", "n.d.", "No date", …),
and a title that merely starts with those words is graded like any other.

## Consequences

- `scripts/hallu_score.py` changes to match; `tests/` checks every rule and
  SPEC.md's worked examples.
- Rule f raises error rates compared with the exploratory scorer, which
  counted a changed character as lost only. Rules c1 and the bug fix also
  raise some scores. Exploratory runs used for comparison are re-scored from
  their saved files under these rules (free; no model calls), and the old and
  new scores are both reported.
- Not decided here, and left as the exploratory scorer had them (weight 0,
  recorded): a spacing or separator change in a list of object numbers
  (`45.24.10, .30a, b` → `45.24.10; .30a; b`), and a blank *date* filled in
  with a placeholder ("n.d."). Raised with the repo author.
- Spec v1.1's "may change" list doesn't include rules a, b, c2 or d. The
  spec gets a version bump (v1.2) with a dated note before it's cited in a
  report (CLAUDE.md).
