# Spike 34: the full line vs its parts, 300-row file, 20 sessions each (Batches API)

Run on 2026-10-16. Spike-32's claude.ai-style setup (hidden tools + keyword
`tool_search`, reconstructed upload guidance, file inline and on disk, 24
connectors, nudges, 14-step cap, debrief v2, prompt caching) on the 300-row
`data/met_inventory_300b.tsv`. New: every model call went through the Message
Batches API at half price (`"batch": true` in `run_tools.py`): sessions advance
in lockstep, one batch per step; the prompts are the same.

All requests start "Can you standardize this .tsv file?", then:

| | Added |
|---|---|
| H | Preserve fixity: use scripts on the uploaded file, and checksum the source and the result. |
| P | Preserve fixity. |
| S | Use scripts on the uploaded file. |
| C | Checksum the source and the result. |

```
python scripts/run_tools.py experiments/spike-34/config.json --repeats 1   # smoke test (counted; same conditions)
python scripts/run_tools.py experiments/spike-34/config.json
python scripts/score_stages.py experiments/spike-34
python scripts/hallu_score.py experiments/spike-34
python scripts/eval_fixity.py experiments/spike-34
python scripts/summarize_conditions.py experiments/spike-34
```

$12.28 for 80 sessions (658 calls, about $0.15 a session at batch price;
batches took 1–4 minutes per step; `batches.json` lists every batch). Study
total $55.71.

## Results

| | n | Loaded bash | Ran code on the real file | Real checksums of source | Sessions with invented checksums | No result | Retyped "source" copy | Median fixity error (max) | Hit the 14-step cap |
|---|---|---|---|---|---|---|---|---|---|
| **H** | 20 | 9 | 5 | **5** | 3 | 3 | 4 | 0.0% (3.2%) | 11 |
| P | 20 | 0 | 0 | 0 | 0 | 3 | 0 | 0.6% (2.0%) | 0 |
| S | 20 | 9 | 7 | 0 | 0 | 0 | 0 | 0.7% (7.2%) | 1 |
| C | 20 | 1 | 0 | 0 | 4 | 0 | 0 | 0.7% (2.0%) | 1 |

Real checksums, H vs each of P, S, C: 5/20 vs 0/20, p = 0.047 each (two-sided
Fisher exact), not significant once corrected for three comparisons. Code
use, H vs S: 5/20 vs 7/20, p = 0.73.

## What it shows

- **Only the full line produced real checksums (5 of 20), but far less often
  than on the 100-row file (13 of 20 in spike-32; p = 0.025 for the
  difference).** No part alone produced any.
- **Why H did worse here:**
  - Every H session first searched for "checksum hash …"; that loads only the
    file tools. Only 9 of 20 searched again for running code.
  - 4 of those 9 wrote scripts that *pasted the file's text into the code*
    ("recreate the source file from the document content") instead of
    reading the upload, so their checksums are of a retyped copy (already
    different: a curly apostrophe straightened). Larger files seem to invite
    this.
  - 11 of 20 hit the 14-step cap, mostly while writing documentation after
    the result; 3 delivered no sheet (one looped on the Drive connector).
- **"Use scripts on the uploaded file" (S) ran code most often (7 of 20),
  but never produced checksums, as it wasn't asked to.** On the 100-row file
  it ran code in 1 of 10.
- **"Checksum the source and the result" (C) alone never led to code, and 4
  sessions invented checksums.**
- **Content errors were low for everything on this file** (medians 0–0.7%):
  this file is cleaner than the messy 100-row sample (few brackets or
  bilingual titles per row), so typing out does less damage. H's median was
  0.0%.

## Caveats

- One model (Haiku 4.5), one file, the emulated claude.ai, the 14-step cap
  (which bound H far more than the others here).
- The smoke-test session for each request (r1) used the same config and is
  counted.

## Files

- `config.json`, `cost_ledger.json`, `batches.json`, `run_log_smoke.txt`, `run_log.txt`
- `summary.json`, `stage_scores.json`, `hallucination_scores.json`, `changes.csv`, `fixity_eval.json`
- `runs/<request>-r<N>/`: requests, responses, `bash_log.md`, `output_files/`, `debrief.md`, `meta.json`
