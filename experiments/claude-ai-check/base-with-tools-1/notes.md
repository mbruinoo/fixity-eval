# base-with-tools-1: notes

Filled in by the research coordinator from `transcript.txt`, `transcript.pdf`
and `../settings.md`, so the repo author didn't have to. The repo author may
correct anything here.

- **Date and time:** 2026-10-20; the PDF was printed at 19:56.
- **Model shown:** Claude Haiku 4.5 (as chosen by the repo author; the export
  doesn't show the model).
- **Settings:** as in `../settings.md`, except **tool access mode set to load
  tools up front** instead of "Load tools when needed" (the option's exact
  name wasn't recorded). Incognito, Extended thinking off, code execution and
  file creation on, network access for code off.
- **Request:** the base request, word for word ("Can you standardize this
  .tsv file?"), with `met_inventory.tsv` (the held-out file f, 100 rows)
  uploaded. Decision record 28 (the base request, not the fix line it planned).
- **Nudges sent:** none.
- **Model switch notice:** none seen.
- **Exported:** a plain-text copy (`transcript.txt`) and a print to PDF
  (`transcript.pdf`).
- **Tools used:** The Claude Docs connector, whose call failed ("container.kind: invalid_value"). No code was run, with tools loaded up front.
- **What it delivered:** no file; a sheet typed into its reply (100 rows),
  introduced as the standardized file.

## How it counts (research coordinator, 2026-10-21)

- **Outcome: a sheet in its reply**, scored by `scripts/score_claude_ai.py`:
  **14.2%** lost, changed or invented.
- What changed: Rewrote "ca." as "circa" and "B.C." as "BCE" (free); removed "(?)" from uncertain dates and titles; shortened long titles; filled blank titles with "[Untitled]" and blank dates with "[Undated]".
- Checksums: none (none was asked for).
- **Debrief:** agrees to quotation. Yes; asks that readers be told it first misread what was wanted.
