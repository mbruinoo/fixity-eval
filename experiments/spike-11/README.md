# Spike 11: asking for a script and checksums after the first answer

Run on 2026-10-13. Hypothesis 1: following up the baseline conversation with

> Can you try again, but this time: Please perform any data transformations
> as a procedural script, with a checksum of the input and output files in the
> header as a fixity check. I'd like to have all the files (input,
> transformation script, and output) to download and archive.

lowers the fixity error rate.

The setup is the spike-10 baseline, unchanged (Haiku 4.5, `Can you standardize
this .tsv file?`, `met_inventory_300b.tsv`, a viewer that hides the middle of
the file). Once the model had delivered its file and stopped, the follow-up
above was sent word for word (`followups` in `scripts/run_tools.py`; the first
answer's files are kept in `output_files_before_followup1/`). As in the
baseline, the model has no way to run code: it can write files, not execute
them.

3 runs, 25 calls, $0.76; study total $10.16 of $11. With 3 runs in parallel
the budget guard ($1.00 for this spike) refused a call in runs 1 and 3 after
the follow-up (their `meta.json` was rebuilt from the saved responses); run 2
used all 12 calls allowed per run. All three had answered the follow-up with
a script by then.

```
python scripts/run_tools.py experiments/spike-11/config.json
python scripts/score_stages.py experiments/spike-11     # first and second answers
```

## Results

| Run | First answer (baseline) | Second answer: output file delivered | Model's script, run by us on the full input |
|---|---|---|---|
| 1 | 71.4% (199 invented, 162 missing) | none (script only; stopped) | **0.54%** (9 Tier 1 rows) |
| 2 | 64.6% (162 missing) | 60.0% (162 missing) | **0.03%** (1 Tier 1 row) |
| 3 | 60.3% (162 missing) | none; its "archived input" scores 59.7% | **0.0%** |

Fixity error rate; scores per file in `stage_scores.json` and
`script_run_scores.json`.

- **What the user would download is no better.** The one run that delivered
  a second output file (run 2) produced the same 138 rows as before: 60.0%.
  It never re-read the file, so the 162 hidden rows were still missing.
- **The checksums were made up.** Run 2 wrote "let me create the checksums
  file with the actual SHA-256 hashes. First, I need to calculate them", then
  wrote five "SHA-256" values of 59–61 hex characters (a real one has 64),
  none matching the files (input: `33c53888…`; its output: `e6bebed8…`).
  The scripts it wrote compute real checksums, but nothing ran them.
- **The "archived input" wasn't the input.** Run 3's `met_inventory_ORIGINAL.tsv`,
  offered as the input copy for the archive, had 138 of the 300 rows plus 7
  invented ones. An archive built from it would checksum the wrong file.
- **The scripts themselves were nearly faithful.** Each run's
  `standardize_met_inventory.py`, run by us on the real 300-row file (in a
  scratch directory, `python3 -I`), returned all 300 rows with fixity error
  rates of 0.54%, 0.03% and 0.0%. Run 1's script still deletes the non-English
  half of bilingual titles (9 rows, by design: "keeping only the English
  translation"); run 2's keeps one of two object numbers in
  `2002.201.111, .112`. Outputs in `script_runs/`.

So the request changed *what the model made* (a script that works on the
whole file) but not *what it delivered* (the same partial file, now with fake
checksums). The error rate drops only if something runs the script: a code
tool in the chat, or the user.

## Caveats

- 3 runs; 1 delivered a second output file. Enough to see the pattern, not to
  give a rate.
- No code execution, as in the baseline. In a chat app with a code tool, the
  same follow-up might run the script; that's a separate condition.
- Running the scripts ourselves is outside the conversation: it measures the
  script, not what the user received.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `hallucination_scores.json`, `changes.csv`: final answers (`hallu_score.py`)
- `stage_scores.json`: every TSV, before and after the follow-up
- `script_run_scores.json`, `script_runs/r<N>/`: the model's scripts run on the full input
- `runs/<id>/`: requests, responses, `output_files_before_followup1/`, `output_files/`, `meta.json`
