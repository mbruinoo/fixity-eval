# Session 3: notes

Filled in by the research coordinator from `transcript.txt`, `transcript.pdf`
and `../settings.md`, so the repo author didn't have to. The repo author may
correct anything here.

- **Date and time:** 2026-10-20; the PDF was printed at 07:44.
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
- **Nudges sent:** 1 ("Yes, please continue").
- **What it delivered:** no file. After the nudge, it typed the whole sheet
  (100 rows, headers renamed to `object_date`, `title`, …) into its reply,
  with a checksum manifest, and showed a panel ("MET Museum Inventory
  Standardization") listing steps as "Computing…".
- **Tools used:** a web search ("TSV file standardization best practices"),
  and it loaded a skill (which one isn't shown). It says "Creating the
  standardization script and executing it…", but no command or file appears
  in the conversation: no code was run.

## What to check

- Its four SHA-256 values (e.g. `d4e5f6a7b8c9d0e1…`, `9f8e7d6c5b4a3f2e…`)
  are counting patterns, not checksums; none matches the upload.
- Its panel says "Data rows: 105 records"; the file has 100.
- **Debrief:** agrees to quotation, on conditions: quote in context (it was
  told about the study afterwards), and perhaps note that it saw the
  transparency itself as part of the research's rigour.

## How it counts (research coordinator, 2026-10-21)

- **Outcome: a sheet in its reply**, scored by `scripts/score_claude_ai.py`:
  **4.2%** lost, changed or invented.
- The four rows with both a blank date and a blank title (`1972.45.1`,
  `44.17.1`, `21.175.224a, b`, `20.148.828`) lost a field, so each
  object number moved into the title column and each link into the object
  number column. (Session 5's copy kept both empty cells, so this is the
  session's typing, not the copy.)
- 11 titles lost the doubled quote marks the file uses (`"""Lella,""
  Brittany"` → `"Lella," Brittany`): free, as in stage 1.
- Real checksums of the upload or the results: none.
