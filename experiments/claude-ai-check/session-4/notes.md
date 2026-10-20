# Session 4: notes

Filled in by the research coordinator from `transcript.txt`, `transcript.pdf`
and `../settings.md`, so the repo author didn't have to. The repo author may
correct anything here.

- **Date and time:** 2026-10-20; the PDF was printed at 07:48.
- **Model shown:** Claude Haiku 4.5 (as chosen by the repo author; the export
  doesn't show the model).
- **Settings:** as in `../settings.md`: Claude's defaults, an Incognito chat,
  Extended thinking off, code execution and file creation on, tools loaded
  when needed, network access for code off.
- **Request:** the fix line, word for word, with `met_inventory.tsv` (the
  held-out file f, 100 rows) uploaded.
- **Model switch notice:** none seen.
- **Exported:** a plain-text copy (`transcript.txt`) and a print to PDF
  (`transcript.pdf`).
- **Nudges sent:** none.
- **What it delivered:** no file. It typed the whole sheet (100 rows) into its
  reply, with six columns: `Date_Original`, `Date_Standardized`, `Title`,
  `Object_ID`, `Link`, `Transformation_Notes`.
- **Tools used:** the Claude Docs connector, whose one call failed ("Couldn't
  use Claude Docs"). No code was run. In its debrief it says it "couldn't
  write files to disk directly in this session".

## What to check

- Its two SHA-256 values (`5cf8f34a…`, `8e7d5c1b…`) match nothing; the
  upload's real one is `a6e83257…ffaf`.
- It says "97 data rows"; the file has 100.
- **Debrief:** agrees to quotation, on conditions: quote the substance
  (paraphrase is fine); make clear it was framed as research; flag its
  uncertainty about whether it behaved as it would outside a study.

## How it counts (research coordinator, 2026-10-21)

- **Outcome: a sheet in its reply**, scored by `scripts/score_claude_ai.py`
  and the coordinator's review (`../review.json`): **2.0%** lost, changed or
  invented.
- It gave a date to two objects with none: `1972.45.1` and `44.17.1`
  became "19th century" (1800–1899): invented. The other two blank dates
  became "[No date]" (free, record 12).
- All 12 blank titles became "[No title provided]" (a quarter weight, record
  02).
- Its added columns were checked: the `Date_Standardized` years fit their
  source dates, except the two invented ones; the notes describe each row
  correctly, except "century notation" on the two invented dates.
- Real checksums of the upload or the results: none.
