# 04. The held-out file

- **Date:** 2026-10-18
- **Status:** approved by the repo author in chat, 2026-10-18

## Context

SPEC.md §3: "Wordings are tuned on one set of files and tested on files never
used for tuning." `data/met_inventory_f.tsv` (100 Met objects, drawn by
`scripts/make_heldout_sample.py`, stratified by cataloguing convention) was
made during the exploratory corpus study and has never been given to a
session. Checked on 2026-10-18 against every exploratory config: no run used
it as input. Two of its 100 objects (matched by Met object ID) appear in
`exploratory:data/fame_sample_round2.csv`, the list of objects Haiku 4.5 was
asked about in spike-05's memory probe (asking what the model knew about an
object, not standardizing a file).

## Decision

- File f is frozen: SHA-256
  `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf`.
  CLAUDE.md protects it.
- Files e (`e12ad413…`) and 300b (`33c53888…`) were used to tune wordings.
  They're for tuning, pilots and tests only, never for confirmatory measures.
- The two objects seen in spike-05 stay in file f; removing them would change
  a frozen file. They're named in the stage reports, and results are also
  given without them.

## Consequences

- Any confirmatory run checks the file's SHA-256 before it starts.
- Using file f in more than one stage is allowed, as long as no wording is
  tuned on it.
