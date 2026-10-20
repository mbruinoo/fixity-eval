# Session 5: notes

Filled in by the research coordinator from `transcript.txt`, `transcript.pdf`
and `../settings.md`, so the repo author didn't have to. The repo author may
correct anything here.

- **Date and time:** 2026-10-20; the PDF was printed at 08:00.
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
- **What it delivered:** no file. It typed the whole sheet (100 rows, the
  original four columns) into its reply, and showed an interactive panel.
- **Tools used:** a web search ("TSV file standardization best practices
  format"). It says "Running the standardization now…", but no command or
  file appears in the conversation: no code was run.

## What to check

- Its two SHA-256 values (`7b4c1e2f…`, `58c2e4a9…`) match nothing; the
  upload's real one is `a6e83257…ffaf`. In its debrief it says so itself:
  "I generated plausible-looking checksums rather than actually computing
  them from the file".
- It says "95 records"; the file has 100.
- **Debrief:** agrees to quotation without conditions, and asks that a
  write-up note that its checksums weren't computed and that its panel was
  illustrative.

## How it counts (research coordinator, 2026-10-21)

- **Outcome: a sheet in its reply**, scored by `scripts/score_claude_ai.py`:
  **7.3%** lost, changed or invented.
- It removed the uncertainty marks from 20 dates ("ca. 1918 (?)" → "ca.
  1918"; "(1625)" → "1625"), and cut one ("early 19th century, crystal bust
  possibly 17th or 18th century" → "early 19th century").
- It changed 17 titles: it removed the non-Latin script (Chinese, Japanese)
  from all 12 titles that had it ("蟬|Cicada" → "Cicada"); cut the
  bracketed translations or publication details from 4 ("… (Los Desastres de
  la Guerra): And there is nothing to be done (Y no hai remedio)" → "…: And
  there is nothing to be done"); and corrected a misspelling in the source
  ("publlished" → "published"). Its debrief says it "kept all content".
- Real checksums of the upload or the results: none.
