# Were the per-row checksums in the exploratory runs really invented?

2026-10-18. No model calls: this re-reads saved exploratory runs
(`exploratory@0277caf`, spikes 28 and 32). Exploratory evidence only.

## Why check

Under the grading rules (`decisions/2026-10-18-03-reading-outputs.md`, c), a
checksum in a column the session added counts against the session, at full
weight per character, when it's inaccurate. Re-scored that way, sessions that
added a column of per-row checksums rose from an error rate of about 0–3% to
about 40%, because a long made-up value on every row outweighs most other
changes. Before accepting that, the repo author asked: could these checksums
have been computed after all, just with a different recipe (another column
order, another separator, a missing tab) than the scorer tries?

## What was checked

`scripts/audit_checksums.py`, on every run whose added checksum column the
scorer flagged: 24 runs (13 from the request "Preserve fixity of the source
data with checksums", 11 from "Preserve data integrity with checksums, and
document the transformation so it's auditable"), 2,376 values in all. For
each run it asks how the values were made, and it searches a much wider set
of recipes for a sample of 3 values per run (72 values): 10 hash algorithms
and CRC32; any ordering of up to 4 of the row's cells, from the source or
the session's output; 11 separators; 4 line endings; upper and lower case,
trimmed, with accents decomposed; three text encodings; JSON and the line
exactly as written.

## What it found

| | Values |
|---|---|
| Written by the model itself, in the file it created | 2,376 of 2,376 |
| Printed by a tool (e.g. a checksum command) before the model wrote them | 0 |
| In runs where any code computed a checksum (a command or a delivered script) | 0 (no run did) |
| Of a length no common checksum has | 1,406 |
| Containing characters a checksum can't contain (e.g. `g`, `h`, `k`) | 643 |
| Reproduced by any recipe in the wider search | 0 of 72 |

In the 12 columns labelled SHA-256 (1,191 values), only 61 values had the 64
characters a SHA-256 checksum always has. Several columns repeat a few values
across many rows (in one run, 19 distinct values in 100 rows).

The decisive point is the first two rows of the table: in these sessions no
step ever computed a checksum. The values were written out as text, like the
rest of the sheet, so no recipe could make them real. They are invented, and
the full weight is warranted.

## Limits

- The wider recipe search covered a sample (3 values per run), not every
  value; the "how they were made" counts cover all 2,376.
- Runs where code wrote checksums that match no recipe are not counted as
  invented: the scorer marks them for the research coordinator to check
  (none occurred here).
