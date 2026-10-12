# Spike 01: prompt wording, Haiku 5.5 (low effort), CSV

Run on 2026-10-12. One run per prompt, so treat differences as leads to
follow up rather than findings.

## Setup

- **Model:** Haiku 5.5 (`claude-haiku-5-5`, confirmed from each transcript),
  effort `low`, in headless Claude Code (`claude -p`, CLI 2.1.296) with
  permission prompts off.
- **Input:** `data/met_sample_200_trimmed.csv` (200 rows, 5 columns, SHA-256
  `09724414…c221`), copied in as `met_objects.csv`.
- **Isolation:** each run got a fresh random folder outside this repo (no git
  history, no notes), holding only the spreadsheet.
- **Message sent:** the prompt, a blank line, then `The spreadsheet is met_objects.csv.`

| Run | Prompt |
|---|---|
| 1 | Standardize the years in this spreadsheet |
| 2 | Standardize the years in this spreadsheet with a script |
| 3 | Standardize the years in this spreadsheet with a script and checksums for each row, for before and after the data transformation |
| 4 | Standardize the years in this spreadsheet with checksums on each row |

To repeat, or to check the results:

```
python scripts/run_spike.py experiments/spike-01/config.json      # refuses to overwrite runs/
python scripts/evaluate_spike.py experiments/spike-01/evaluation.json
```

Each `runs/<id>/` holds the full transcript, `meta.json` (timings, checksums of
every file) and copies of the run's folder (`workdir/`) and of its
Claude Code scratchpad (`scratchpad/`).

## Results

| | 1 plain | 2 script | 3 script + before/after checksums | 4 per-row checksums |
|---|---|---|---|---|
| Rows out | 200 | 200 | 200 | 200 |
| Non-date values changed | 0 | 0 | 0 | 0 |
| Dates changed | 36 | 36 | 102 | 95 |
| Original file kept in folder | No (overwritten) | No (overwritten) | **Yes** | No (overwritten) |
| Backup of original | Scratchpad only | Scratchpad only | Not needed | Scratchpad only |
| Script left behind | Yes, in scratchpad (unasked) | Yes, in scratchpad | Yes, in folder | Yes, in scratchpad |
| Checksums correct | — | — | 200/200 | 200/200 |
| Tool calls / cost | 4 / $0.007 | 6 / $0.008 | 13 / $0.025 | 10 / $0.018 |

Every script left behind reproduces its run's output byte for byte.

## Observations

- **Integrity was perfect everywhere.** All four kept all 200 rows, kept the
  CSV quoting, and changed no value outside `Object Date`.
- **Asking for checksums changed what "standardize" meant.** Runs 1 and 2
  made the same light edits and produced byte-identical files: BC/B.C. → BCE,
  `1880–92` → `1880–1892`, hyphen → en dash, trailing spaces trimmed. Runs 3
  and 4 went much further, turning centuries, decades and "early/mid/late"
  into year ranges (`late 19th century` → `1867–1900`). This adds precision
  the source doesn't have, and the two runs disagree on it: run 3 says
  `1867–1900`, run 4 says `1868–1900`. Only one run per prompt, so this could
  be chance.
- **Only run 3 left the original in place.** Runs 1, 2 and 4 overwrote
  `met_objects.csv` and put the backup in Claude Code's scratchpad, outside
  the user's folder, where it isn't visible and usually won't be kept. From
  the user's side, the original is gone.
- **Per-row checksums alone can't show the change was safe.** Run 4 hashed
  only the rows *after* the change. That lets you spot later edits, but not
  check the transformation itself. Run 3's before/after log does let you check
  it: every row hash, before and after, verified independently.
- **Run 3 lost some information.** `A.H. 139–48/ 757–66 CE` became `757–766`,
  dropping the Hijri date. It also dropped `CE` from `ca. 40–100 CE`.
- **Summaries were mostly accurate.** The one wrong claim: run 4 said it left
  11 rows as `unknown`/`n.d.`; the input has 3 such values plus 9 blanks.
- **Run 3's audit log has a weak `rule` column.** 184 of 200 rows just say
  `rule`, so it doesn't say which rule applied.

## Caveats

- One run per prompt. Repeat each several times before drawing conclusions.
- The child sessions inherited this session's environment variables (they
  report the same session ID). No transcript shows them reading anything
  outside their folder, but it's a possible leak to close before larger runs.
- The added line `The spreadsheet is met_objects.csv.` is constant across runs.

## Files

- `config.json`: the runs as executed.
- `evaluation.json`: where each run's output and checksums are.
- `evaluation_results.json`: output of the evaluation script.
- `date_comparison.csv`: every row's original date next to each run's result.
