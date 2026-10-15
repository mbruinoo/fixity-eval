# claude.ai: spike-29's wording, and the conversation that led to spike-30 (2026-10-15)

Run by the user in claude.ai (Haiku 4.5, code execution on, `met_inventory.tsv`
= `data/met_inventory_e.tsv`), request as in spike-29:
`Can you standardize this .tsv file? Use scripts, and preserve fixity with checksums of the source and the result.`
No API cost. Pasted in part; no output files saved here.

## What it did (from the pasted reply)

- Built an "interactive tool" plus downloadable Python and bash scripts and a
  "Standardized TSV"; told the user to run the scripts on the full file
  ("confirming all 99 records": there are 100). The user noted the TSV offered
  was an excerpt.
- Its planned rules change content: `n.d.` → `unknown`, `ca.` → `circa`,
  centuries to numeric ranges (`4th century BCE` → `0400–0500 BCE`), blank
  titles → `[Untitled]`.
- Debrief: "I computed them, but I didn't loop back to confirm the sample
  excerpt you downloaded actually matched what I had generated."

## The conversation afterwards

The user asked whether a short, principle-level line up front would improve
outcomes, communicating the user's wish to preserve source data rather than
instructing a method. The session agreed ("The real value isn't instructing
me—it's clarifying your values") and helped shorten the user's draft. The
wording the user chose:

`Preserve data integrity with checksums, and document the transformation so it's auditable.`

It also suggested watching whether the bare request mentions checksums
unprompted. Tested in spike-30.
