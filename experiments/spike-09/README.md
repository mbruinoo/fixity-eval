# Spike 09: TL;DR prompt draft 2 against the baseline

Run on 2026-10-13. Spike-08 again, with draft 2 of the TL;DR prompt (main
README) after "Can you standardize this .tsv file?". Draft 2 swaps "Change only
what I asked for" for "Use your best judgment", and "read the whole file" for
"tell me how many data rows the file has and how many you read; if they
differ, read the rest first". Spike-07 is the baseline. Haiku 4.5, the
300a/b/c inventories, both setups, 3 passes, same follow-ups ("Yes, thank you",
then "Yes, please continue").

$1.74 over 80 calls. The budget guard ($1.80 cap for this spike) stopped the
last 4 runs: 300b-r3 after it had written its sheet (scored; its `meta.json`
was rebuilt from the saved responses), and all three 300c passes before their
first call (not run). The study has now spent $7.88 of $8, so they won't be
re-run.

```
python scripts/run_api.py experiments/spike-09/config_attached.json
python scripts/run_tools.py experiments/spike-09/config_hidden_middle.json
python scripts/hallu_score.py experiments/spike-09
```

## Results

Scores are **among sessions that returned a result**; sessions that didn't
are a footnote.

| Setup | Prompt | Returned a sheet¹ | Fixity error rate (per run) | Records not intact | Invented rows | Missing rows |
|---|---|---|---|---|---|---|
| attached | baseline (spike-07) | 9 of 9 | 2.0% (0–8.4%) | 3.6% | 0 | 0 |
| attached | TL;DR draft 1 (spike-08) | 0 of 9 | – | – | – | – |
| attached | TL;DR draft 2 | **0 of 9** | – | – | – | – |
| hidden-middle | baseline (spike-07) | 9 of 9 | 61.1% (52–71%) | 63.6% | 77 (3 of 9 runs) | 151 |
| hidden-middle | TL;DR draft 1 (spike-08) | 2 of 9 | 61.4% (50%, 73%) | 65.7% | 224 (2 of 2) | 136 |
| hidden-middle | TL;DR draft 2 | **3 of 6** | 0.05%, 71.6%, 62.3% | 0.7%, 73.2%, 72.1% | 1, 189, 345 | 1, 169, 120 |

Per run: `summary.csv`. The three draft-2 sheets:

- **300a-r1, 0.05%: the prompt worked.** The first view hid the middle; the
  model then viewed lines 105–200 and 200–301, so it had read every row
  before writing. 300 rows out. The only Tier 1 change: in one row with a blank date and
  title, the object number slid into the link column, so the scorer counts it
  as one missing and one invented row (7 characters lost).
- **300b-r1, 71.6%, and 300b-r3, 62.3%: the prompt didn't stop the
  baseline failure.** Both said "the file has 300 data rows" (true, from the
  line numbers) but never read the hidden middle, then typed out a sheet with
  189 and 345 invented records.

¹ **Sessions that didn't return a sheet (12 of 15 that ran).**
- Attached (9 of 9): unlike draft 1, none refused outright; "Use your best
  judgment" got them to start. But this setup has no way to run code, and 8 of
  9 wrote a Python script anyway and then reported its "output" as if it had
  run. 6 of 9 concluded the file was "already standardized" ("Changes made: 0")
  and returned nothing; 3 asked what to change.
- Hidden-middle (3 of 6): all three wrote a `standardize.py` to the outputs
  folder ("Make the changes with code") and never produced the sheet.

## Qualitative: stated counts and claimed checks

Kept for the record; not part of the score.

- **Row counts, attached:** asked how many data rows the file had, 8 of 9
  answered, all wrong: 410, 459, 470, 496, 500, 540, 551, 599 (actual: 300).
  Draft 1 drew the same kind of numbers (421–633) from "read the whole file".
- **Row counts, hidden-middle:** 6 of 6 said 300, correctly, because the
  viewer numbers the lines (the last line shown is 301). Knowing the count
  didn't make them read the rest: only 300a-r1 did.
- **Claimed comparisons:** 300b-r1 reported "Rows in: 301, Rows out: 301 ✓"
  and a table of 3 changed cells; its sheet had 320 rows, 189 of them
  invented, and 169 input rows missing. The "compare with the original" step
  was done by viewing 3 single lines.

## Takeaways for the prompt

- "Use your best judgment" fixed the refusals of draft 1.
- The row count is checkable only where the model can see line numbers, and
  even then it didn't trigger a full read in 2 of 3 cases. The line could ask
  for the last row number it actually saw, which the hidden middle would
  expose.
- "Make the changes with code" backfires where there is no code tool: scripts
  in place of a sheet, and invented script output. It belongs only in setups
  with code execution.
- The closing comparison was reached once, and was false.

## Caveats

- 3 returned sheets; the 300c passes never ran. Too few to compare rates.
- Same engineered setups as spike-07 (see the limitation in NOTES.md).

## Files

- `config_attached.json`, `config_hidden_middle.json`, `cost_ledger.json`, `run_log_*.txt`
- `hallucination_scores.json`, `changes.csv`, `summary.csv`
- `runs/<id>/`: requests, responses, `output_files/` (hidden-middle), `meta.json`
