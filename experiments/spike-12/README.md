# Spike 12: the script-and-checksum follow-up, with a code tool

Run on 2026-10-13. Spike-11 again (Haiku 4.5, `Can you standardize this .tsv
file?`, `met_inventory_300b.tsv`, then the same follow-up asking for a
procedural script, input and output checksums, and all files to archive),
with one change: the file is uploaded into Anthropic's code-execution sandbox
(`attach: upload`, `tools: code_execution`) instead of shown through our
hidden-middle viewer. The model reads and writes the file with code. 1 run.

```
python scripts/run_api.py experiments/spike-12/config.json
python scripts/score_stages.py experiments/spike-12
```

`run_api.py` gained `followups_after_delivery`: sent once a file or table has
arrived and the model has stopped (the earlier files move to
`output_files_before_followup1/`). The older `followups` key, used by spike-03,
is unchanged.

## Result

| | First answer | After the follow-up |
|---|---|---|
| Fixity error rate | **0.0%** (300 rows, 0 invented, 0 missing) | **0.0%** (byte-identical output file) |
| Tier 3 (not counted) | quotation marks removed from 4 titles | same |
| Checksums | – | **real**: input `33c53888…d547` and output `86ecd210…82ed` both match `sha256sum` |
| Archived input | – | `met_inventory_ORIGINAL.tsv` byte-identical to the upload |
| Code steps | 5 | 39 |
| Cost / time | $0.10, 26 s | **$2.55, 10 min** |

- **With a code tool, the baseline failure doesn't happen.** The model read
  the whole file with code and wrote it with code: no dropped rows, no
  invented ones. It also reordered the columns and quoted every field
  (not graded; the scorer matches columns by name).
- **The follow-up produced a genuine fixity record.** Script, log, README,
  manifest and verification file, with checksums computed by code and correct.
  The standardized file it re-made is the same, byte for byte, as the first.
- **But it was expensive.** In the follow-up turn the model ran 39 code steps
  inside a single API request. Each step re-sends the whole conversation
  (including file contents and earlier output), so that one request used 2.3
  million input tokens: $2.55, 25× the first answer. Many steps went to
  copying files into the outputs folder again and again ("I see - the
  OUTPUT_DIR changes between bash calls. Let me copy everything in one
  go"), and to writing four overlapping summary files.

## Budget note

The cost guard checks before each request; it can't see the cost of the steps
the sandbox runs inside a request. This spike's cap was $1.00 and it spent
$2.65. Study total: $12.81 of the $13 limit. Any future sandbox run needs a
per-run cap well above the expected cost, or a limit on code steps.

## Caveats

- 1 run. It shows the follow-up *can* work with a code tool, not how often.
- It isn't a refinement of the baseline: the code tool removes the hidden
  middle, which is what makes the baseline fail. The spike-03 sandbox runs
  (condition 41, 100 rows) also invented nothing.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `hallucination_scores.json`, `changes.csv`: final answer; `stage_scores.json`: both answers
- `runs/sandbox-followup-r1/`: requests, responses, `output_files_before_followup1/`,
  `output_files/` (all 13 files the model made), `meta.json`
