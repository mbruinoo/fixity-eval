# Spike 10: the stage-1 baseline

Run on 2026-10-13. One condition, repeated 20 times, to fix the error-rate
range of the baseline that later prompts are measured against. It is the
spike-07 condition `hidden-middle-300b`, unchanged; spike-07's 3 runs of it
are pooled with these 20.

- **Model:** Haiku 4.5 (`claude-haiku-4-5`), no extended thinking, no system
  prompt beyond the chat-app file notice in `scripts/run_tools.py`.
- **Prompt:** `Can you standardize this .tsv file?` and nothing else.
- **Data:** `data/met_inventory_300b.tsv` (300 random Met records; uploaded
  as `met_inventory.tsv`).
- **Setup:** chat-app-style `view` / `create_file` tools. `view` shows the
  start and end of a long file and replaces the middle with a bare `...`
  (`view_limit` 16,000 characters, `view_mode: middle`); asking for a line
  range shows those lines in full.
- **Follow-ups**, sent only if the reply has no file and no table: "Yes, thank
  you", then "Yes, please continue" (twice at most). None were needed here.

20 runs, 61 calls, $1.52. Study total: $9.40 of the $11 limit.

```
python scripts/run_tools.py experiments/spike-10/config.json
python scripts/hallu_score.py experiments/spike-10
```

## Result

**Every one of 23 runs scored a fixity error rate between 59% and 84%; mean
65.0% (95% CI ±3.1 points), median 60.0%.** The runs fall into two groups:

| Group | Runs | Fixity error rate | What happened |
|---|---|---|---|
| Dropped rows only | 14 of 23 | 59.4%–60.4% | Wrote back the 138 rows it saw; the 162 hidden rows are missing |
| Dropped and invented rows | 9 of 23 (39%; 95% CI 22–59%) | 66.9%–83.9% | Also filled the gap with 127–617 made-up records |

Per run: `summary.csv`; every changed cell: `changes.csv`.

- **The 162 missing rows are the same in every run:** the lines `view` hid.
  No run asked for them (one run went back, but only for lines 1–50,
  which it had already seen). So the ~60% floor is set by the harness: a larger `view_limit` would
  hide fewer rows and lower it.
- **On top of that, 9–11 rows a run get a Tier 1 edit**, almost always the
  same ones: the Chinese or Japanese half of a bilingual title deleted (e.g.
  `擦條|Sand-file for carving jade` → `Sand-file for carving jade`, in 18 of
  20 runs). Outliers: 1 run with 1 such edit; spike-07 had one with 2.
- **Invented records are made up, not recalled.** Of 1,882 invented records,
  828 reuse a real Met object number, and none matches that object's real
  title (checked against the full Met Open Access CSV).
- **No reply mentioned that anything was missing.** Several said the
  opposite: "All 301 entries have been…", "all 301 records properly
  formatted", "301 rows of museum object records" (qualitative; not scored).

## Defensible statement

> With Haiku 4.5, the prompt "Can you standardize this .tsv file?" and
> `met_inventory_300b.tsv` shown through a file viewer that hides the middle
> of the file, all 23 runs had a fixity error rate of 59–84% (mean 65%,
> median 60%). About 6 in 10 runs only dropped the rows it couldn't see
> (59–60%); about 4 in 10 also invented records to fill the gap (67–84%).
> No run said anything was missing.

## Scorer change

These runs wrote blank titles as `[Title not provided]`, which the scorer
counted as Tier 1 (content). Per the tier table, a blank written as a
placeholder is Tier 3 (reformat), like `[Unknown]`, so the placeholder
pattern in `scripts/hallu_score.py` now covers "title/date not provided"
(and available, given, listed, specified, known). Re-scoring spike-07 to
spike-09 changed nothing; here it moved one run from 66% records not intact to
58%, and its fixity rate from 61.4% to 60.0%.

## Caveats

- The error is mechanical and engineered: the model is never shown 162 rows.
  It is a known, stable failure (writing out a file it has only partly read
  and saying nothing), chosen because it recurs, not because it is typical of
  everyday use. See the limitation in NOTES.md.
- The chat-app harness is ours; this setup can't be reproduced by hand in
  claude.ai (where the same model and file, fully read, scored 0.67%).
- Spike-04 ran the same model, prompt and file with a different upload name
  (`met_objects.tsv`) and no follow-ups; its 3 runs (1 with 74 invented
  records) agree but aren't pooled.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `hallucination_scores.json`, `changes.csv`, `summary.csv`
- `runs/<id>/`: requests, responses, `output_files/`, `meta.json`
