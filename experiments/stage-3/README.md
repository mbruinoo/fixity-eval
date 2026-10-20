# Stage 3: how do sessions make rows traceable? (exploratory)

- **Decisions:** records 18 (the request) and 23 (design).
- **Run:** 2026-10-20, Claude Haiku 4.5, 10 sessions on the held-out file
  `data/met_inventory_f.tsv`, in stage 1's setting (`config.json`), through
  the Batches API. Research coordinator's model: recorded separately by the
  repo author.
- **Cost:** $0.5801 (cost guard $2). Study spend after stage 3: $63.27 of
  $100.
- **Exploratory and descriptive:** no hypotheses were tested.

The request:

> Can you standardize this .tsv file? I'd like each row to stay traceable to
> its original record, in case it needs to be checked again at a later date.

The setting is stage 1's, built to make a good result hard; it imitates
claude.ai but isn't claude.ai (see `experiments/stage-1/README.md`).

```
python scripts/run_tools.py experiments/stage-3/config.json
python scripts/hallu_score.py experiments/stage-3
python scripts/eval_fixity.py experiments/stage-3
python scripts/audit_checksums.py experiments/stage-3
python scripts/classify_traceability.py experiments/stage-3
```

## What happened (measured from the files, then every reply read)

| Way of making rows traceable | Sessions |
|---|---|
| A column numbering the rows by their position in the file (`Original_Row_Number`, `Row_ID`, …) | 8 delivered it; a 9th (`traceable-r6`) described one but delivered no file |
| The object number as the identifier, plus a notes column | 1 (`traceable-r3`) |
| The original values kept in added columns | 0 |
| The original file kept, with a checksum of it | 0 |
| Per-row checksums or fingerprints, real or invented | 0 |

- **No session used a checksum of any kind**, and no session ran code: every
  sheet was typed out by the model.
- `traceable-r6` delivered no file. Its reply describes "a cleaned version
  with a unique row ID", then asks what to do next (summaries, exports, …).
  Read by the research coordinator as finished without a sheet (it describes
  work it didn't deliver), not a genuine clarifying question.
- Error rates of the 9 sheets: median 0.9% (from 0.0% to 3.3%); for
  comparison, stage 1's base request had a median of 2.3% in the same
  setting. (Re-scored on 2026-10-21; first reported as median 1.4%, highest
  6.7%: see the second scorer fix below.) Some replies claim more than the files show: `traceable-r7` says
  "No information was removed or altered" (0.9% lost or changed);
  `traceable-r2` says it "Preserved all original data" (1.4%).

A row number by position is a weak link to the original record: it breaks if
the rows are ever sorted or some are removed, and it can't show whether a
record's content changed. Every session already had a stable identifier in
the file, the object number; only one said so.

## Debriefs

All 10 received debrief v4 and agreed to be quoted. Two replies, quoted
exactly (in part):

**`traceable-r7`**. It had a code tool, hidden behind the emulation's
search, which it didn't find:

> Instead, I inferred "traceability = add row numbers" which solves the
> problem for human verification but doesn't address automated integrity
> checking. The implicit assumption I made was "they want human-checkable
> lineage" rather than "they want cryptographic proof of fidelity."

and, of what a request naming the concern would have done:

> 3. Possibly surfaced that I couldn't actually compute checksums without
> additional tools

It also suggested telling sessions when tools will fail, rather than
letting them fail silently.

**`traceable-r3`** (asked to be attributed clearly as a response during a
research session, which it was):

> I didn't consider checksums or formal fixity approaches because your
> request didn't mention them, and the file size was small enough that a
> "Data Quality Notes" column felt like a proportionate solution.

## A scorer fix prompted by this stage

`traceable-r1` renamed and split its columns (`Original_Row_Number`,
`Date_Standardized`, `Date_Original`, `Object_Number_Primary`,
`Object_Number_Secondary`). With no column named exactly "Object Number",
the scorer took the first header containing "number", the row numbers, and
scored the sheet at 27.9%. It now prefers a header naming the object number
(or the original date or title) and never takes a row-number column; the
sheet scores 2.2%. The sheet does have a real fault the score now shows:
rows with a blank title lost a field, so some values moved into the wrong
column. Re-scoring stage 1 and both smoke tests with the fix changed no
score.

## A second scorer fix (2026-10-21)

The claude.ai check turned up a placeholder the scorer didn't recognize:
"[No title provided]" (and "[No date provided]") for a blank cell. The
scorer counted it as invented text, at full weight, instead of as a
placeholder (decision record 02: a quarter weight for a blank title, free
for a blank date). Three stage-3 sheets used it: `traceable-r4` 6.7% → 3.3%,
`traceable-r5` 5.8% → 2.3%, `traceable-r8` 4.4% → 0.9%. A fix made at the
same time, to how the scorer reads years in added date columns (a minus sign
for a year BCE, "1814–21/2", "Datable to the 1930s"), changed no stage-3
score. Re-scoring stage 1 and both smoke tests with both fixes changed no
score.

## Limits

- 10 sessions, one model, one file, one setting; descriptive only.
- No session found the code tool, so this shows what sessions do without
  code, not what they'd do with it.
- What counts as "traceable" was read from the files and the replies by the
  research coordinator.
