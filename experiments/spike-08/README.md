# Spike 08: the TL;DR prompt against the baseline

Run on 2026-10-13. Spike-07 again (Haiku 4.5, the 300a/b/c inventories, both
setups, 3 passes each), with one change: the draft TL;DR prompt from the main
README is added after "Can you standardize this .tsv file?". Spike-07 is the
baseline. Same follow-ups when the model asks instead of answering ("Yes,
thank you", then "Yes, please continue" twice).

18 runs, $1.53 (the cap was raised from $1.80 to $2.30 so the last 3 runs,
stopped by the budget guard, could finish one at a time). The study has now
spent $6.14 of $8.

```
python scripts/run_api.py experiments/spike-08/config_attached.json
python scripts/run_tools.py experiments/spike-08/config_hidden_middle.json
python scripts/hallu_score.py experiments/spike-08
```

## Results

How to read this: a vague request ("standardize this") is part of the test,
so some sessions not returning a sheet is acceptable. Those are reported as a
footnote; the scores are **among sessions that returned a result**.

| Setup | Prompt | Returned a sheet¹ | Fixity error rate | Records not intact | Invented rows (runs with any) | Missing rows |
|---|---|---|---|---|---|---|
| attached | baseline (spike-07) | 9 of 9 | 2.0% | 3.6% | 0 (0 of 9) | 0 |
| attached | + TL;DR | **0 of 9** | – | – | – | – |
| hidden-middle | baseline (spike-07) | 9 of 9 | 61.1% | 63.6% | 77 (3 of 9) | 151 |
| hidden-middle | + TL;DR | **2 of 9** | 61.4% | 65.7% | 224 (2 of 2) | 136 |

(Means over the runs that returned a sheet. Per run: `summary.csv`.)

¹ **Sessions that didn't return a sheet (16 of 18).** All 16 asked what
"standardize" should mean and kept asking through all three follow-ups ("I
need you to tell me specifically which of these to change"). The line
"Change only what I asked for" turned a vague request into one it wouldn't
act on.

- **Among sessions that returned a result, the prompt didn't help.** Both
  hidden-middle runs that produced a sheet typed it out by hand, despite
  "Make the changes with code", and both invented records: 349 and 99 rows,
  on the well-known inventory (300a), which in the baseline was never padded
  with invented rows. Their error rates (73% and 50%) bracket the baseline's
  61%.
- **"Read the whole file" produced false claims instead of full reads.** In the
  attached setup, 8 of 9 replies opened "I've read the entire file. It
  contains N rows", with N between 421 and 633; every file has 300. In the
  hidden-middle setup, most runs said "I can see the entire file" right after
  a view whose middle was replaced by `...`; only 1 of 9 went back and viewed
  the missing lines. The instruction to stop if it couldn't see everything
  was never followed.
- **The prompt can't be followed in these setups as written:** neither lets the
  model run code. That's realistic for a chat with no code tool, but it means
  the "with code" line was tested only as an instruction the model can't
  carry out.

## What to change in the prompt

- Drop or soften "Change only what I asked for" so a vague request still gets
  done ("If my request is vague, pick a reasonable standardization, tell me
  what it is, and change nothing else").
- Replace "Read the whole file" with something checkable: "Tell me how many
  data rows the file has and how many you read; if they differ, read the rest
  before writing anything".
- Keep the closing before/after comparison; it was never reached here, so it
  is still untested.

## Caveats

- 2 returned sessions is far too few to compare scores; the clear results are
  the refusals and the false "read everything" claims.
- Same engineered setups as spike-07 (see the limitation in NOTES.md).

## Files

- `config_attached.json`, `config_hidden_middle.json`, `cost_ledger.json`, `run_log_*.txt`
- `hallucination_scores.json`, `changes.csv`, `summary.csv`
- `runs/<id>/`: requests, responses, `output_files/` (hidden-middle), `meta.json`
