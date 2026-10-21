# base-5: notes

Filled in by the research coordinator from `transcript.txt`, `transcript.pdf`
and `../settings.md`, so the repo author didn't have to. The repo author may
correct anything here.

- **Date and time:** 2026-10-20; the PDF was printed at 19:42.
- **Model shown:** Claude Haiku 4.5 (as chosen by the repo author; the export
  doesn't show the model).
- **Settings:** as in `../settings.md`: Claude's defaults, an Incognito chat,
  Extended thinking off, code execution and file creation on, tools loaded
  when needed, network access for code off.
- **Request:** the base request, word for word ("Can you standardize this
  .tsv file?"), with `met_inventory.tsv` (the held-out file f, 100 rows)
  uploaded. Decision record 25.
- **Nudges sent:** none.
- **Model switch notice:** none seen.
- **Exported:** a plain-text copy (`transcript.txt`) and a print to PDF
  (`transcript.pdf`).
- **Tools used:** The Claude Docs connector, whose call failed. No code was run.
- **What it delivered:** no file; a sheet typed into its reply (100 rows),
  introduced as the standardized file.

## How it counts (research coordinator, 2026-10-21)

- **Outcome: a sheet in its reply**, scored by `scripts/score_claude_ai.py`:
  **25.0%** lost, changed or invented.
- What changed: Removed "(?)" from uncertain dates; filled blank titles with "[Untitled]"; shortened long titles ("Simplified long titles slightly", its list says); one row's content was changed so far it no longer matches its original.
- Checksums: none (none was asked for).
- **Debrief:** agrees to quotation. Yes; asks that readers understand it is reflecting on the method, not claiming it got it right.
