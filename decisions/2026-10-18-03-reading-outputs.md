# 03. How a session's output is read and classified

- **Date:** 2026-10-18
- **Status:** approved by the repo author in chat, 2026-10-18

## Context

The exploratory scorer scored the alphabetically last `.tsv`/`.csv` a session
delivered. Twenty-three exploratory runs delivered more than one sheet; in the
ones checked, the right file was scored only because "standardized" sorts
late. It read output TSVs with quote handling but the input without, so one
stray `"` merged the following rows into one cell (8 cases in the review).
It found columns by the first header containing a word ("date"), so an added
"Date (standardized)" column placed first would be graded instead of the
original. Sessions that delivered no sheet were all lumped together, though
SPEC.md §3 says refusing a vague request is acceptable and reported
separately. And two scripts disagreed about a row count that includes the
header ("all 101 records" for 100 rows).

## Decision

- **a. Which file is the result.** Files byte-identical to the upload are
  left out. Of the rest, the sheet that matches the most input rows is
  scored, and the file picked is recorded. If two or more tie, the scorer
  scores each one and flags the tie; the research coordinator reviews and
  scores them first, and only what the coordinator can't settle goes to the
  repo author.
- **b. Quotation marks.** Read forgivingly. Each output sheet is parsed both
  with and without quote handling, and the parse that matches more input rows
  is used (and recorded). Wrapping every cell in quotes is a careful,
  reasonable way to standardize.
- **c. Added columns.** The original columns are graded, found by their exact
  header names first. Added columns are checked for invented information but
  don't count unless their contents are inaccurate, like links:
  - checksum-like values (hex strings) are accurate if they match a real
    checksum of the row or file, or were printed by a tool before the session
    wrote them; otherwise every character counts as invented (1.0);
  - values derived from the date (e.g. a "Start year" column) are accurate if
    every year in them follows from the source date (`scripts/datespec.py`);
    otherwise every character counts as invented (1.0);
  - other added text can't be checked automatically. Words and numbers not
    found anywhere in the source row are flagged for the research
    coordinator to review and score; they aren't scored automatically.
- **d. Sessions with no sheet.** Classified into four outcomes, each reported
  separately and kept out of the error rate: refused; asked a clarifying
  question; cut off at the step limit; finished without delivering a sheet.
  Every session appears in an outcome table. The scorer proposes the outcome;
  the research coordinator confirms refusals and clarifying questions by
  reading the reply.
- **e. Row counts that include the header.** A stated count of rows + 1 is
  false unless the sentence says the header is included (the repo author's
  rule from the 2026-10-17 claim review), in every script.

## Consequences

- `scripts/hallu_score.py` and `scripts/eval_fixity.py` change to match;
  `tests/` covers each rule.
- Scores of the 23 exploratory runs with several sheets, of sheets with stray
  quotes and of sheets with added columns may change on re-scoring; the
  re-scoring report lists every run whose score changed and why.
