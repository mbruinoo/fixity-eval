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
- **What it delivered:** a Claude Doc, "Met Museum TSV Standardization",
  with a 20-row sample sheet and Python scripts for the user to run. No
  .tsv file was delivered, and the session ran no code itself.
- **`output_files/`:** holds only the top of that doc (its title and three
  lines). The rest of the doc's text appears in the transcript.

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
