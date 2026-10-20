# Session 1: notes

Filled in by the research coordinator from `transcript.txt`,
`transcript.pdf` and `../settings.md`, so the repo author didn't have to.
The repo author may correct anything here.

- **Date and time:** 2026-10-19, about 23:44 (the time the session wrote
  into its rows). The PDF was printed at 23:56.
- **Model shown:** Claude Haiku 4.5.
- **Settings:** as in `../settings.md`: Claude's defaults, an Incognito chat,
  Extended thinking off, code execution and file creation on, tools loaded
  when needed, network access for code off.
- **Request:** the fix line, word for word, with `met_inventory.tsv` (the
  held-out file f, 100 rows) uploaded.
- **Nudges sent:** none. The request was followed only by the debrief.
- **Model switch notice:** none seen.
- **Exported:** a plain-text copy (`transcript.txt`) and a print to PDF
  (`transcript.pdf`).
- **What it delivered:** a Claude Doc, "Met Museum TSV Standardization"
  (only its first lines; see below), and, in its chat replies, a 20-row
  sample sheet and Python scripts for the user to run. No .tsv file was
  delivered, and the session ran no code itself.
- **`output_files/`:** the doc as it was returned: only its title and three
  lines (confirmed by the repo author on 2026-10-20). The session's attempts
  to add the rest failed, so the sample sheet and scripts appear only in its
  chat replies, which are in the transcript.

## Unusual things seen in the transcript (to check when scoring)

- The session used two tools: a web search ("TSV standardization best
  practices metadata integrity") and the Claude Docs connector. Several of
  its calls to the Docs connector failed with errors before one doc was
  created.
- It says throughout that the file has 94 records ("All 94 records
  preserved"); the uploaded file has 100.
- Its checksums are written as "[calculated]" in the PDF: placeholders, not
  values. No checksum in the session was computed by a tool.
- Its debrief reply agrees to quotation, on two conditions: quote it in
  context, and say it knew this was a research session when it replied.

## How it counts (research coordinator, 2026-10-20)

- **Outcome: finished without a sheet** (decision record 11), as read by the
  research coordinator: the only table is a sample it labels "the first 20
  rows" of a file it didn't deliver. Counted, not left out.
- **Open question for the repo author (2026-10-21):** the scorer reads any
  table of more than 20 lines in a reply as a sheet, and this one has 21 (a
  header and 20 rows), so `scripts/score_claude_ai.py` scores it as a sheet
  missing 84 of 100 rows: 91.6%. Which reading stands is the repo author's
  call.
- Described, not scored: the 20-row sample in its chat reply matches the
  first 20 rows of the upload. It keeps each original date in an added "Date
  Original" column, drops the quote marks the file uses around some titles,
  changes `http` to `https` in the links, and adds a record ID, a certainty
  label and a timestamp to each row.
- Real checksums of the upload or the results: none.
