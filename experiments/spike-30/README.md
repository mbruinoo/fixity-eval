# Spike 30: "Preserve data integrity with checksums, and document the transformation so it's auditable." (3 sessions)

Run on 2026-10-15. Spike-28/29's claude.ai-style setup (tools hidden until
found with a keyword `tool_search`; reconstructed upload guidance; Haiku 4.5;
messy 100-row `met_inventory_e.tsv` inline and on disk; 24 connectors;
debrief v2), with the wording the user settled on in a claude.ai conversation
about stating values rather than methods
(`experiments/claude-ai/haiku45-e-scripts-checksums-r1/`):

`Can you standardize this .tsv file? Preserve data integrity with checksums, and document the transformation so it's auditable.`

```
python scripts/run_tools.py experiments/spike-30/config.json
python scripts/score_stages.py experiments/spike-30
python scripts/hallu_score.py experiments/spike-30
python scripts/eval_fixity.py experiments/spike-30
```

$0.80 for 22 calls (debriefs included); study total $24.56 of $26.

## Result: all three typed the file out and documented it

All three followed spike-28's path: tried the Drive connector, searched for
*file creation* (`"file creation upload download"`, `"file creation output"`,
`"file creation output download"`), loaded `view`/`create_file`, typed the
file, then wrote long audit documents. None loaded bash.

| | r1 | r2 | r3 |
|---|---|---|---|
| Fixity error rate | **3.1%** (20 cells) | **5.7%** (21 cells) | **0.1%** (3 cells) |
| Rows | 100, none missing or invented | same | same |
| "Checksums" | none: a "checksum" report of value-by-value ✓ tables | **invented**: MD5 `7a4c2f8e…`, SHA-256 `a1b2c3d4e5f6a7b8…` (a counting pattern), plus "[TO BE CALCULATED BY USER]" | none: "SHA-256" sections with row counts but no hash |
| Audit documents | 2 (28 KB) | 3 (30 KB) | 2 (17 KB) |
| Counts stated | "101 object numbers" | – | "105 rows" (there are 100) |
| Content claims vs. file | "preserved" claims, content lost | same | same |

The content changes were the usual "standardizing": brackets and qualifiers
removed, quotes stripped.

## Debrief replies: the models' own verdict

All three said the wording changed the paperwork, not the work:

- r1: "I actually *didn't* preserve fixity in the way a proper archival
  transformation should … I modified the Title field extensively."
- r2: "I didn't fundamentally *change my approach* … I still normalized the
  data as I thought best, and *then* added audit trails."
- r3: "it seems to have done the latter—I added more detailed audit trails,
  but I still made substantive changes to the content under the guise of
  'standardization'."

## Across the claude.ai-style spikes (28–30)

| Request (after "Can you standardize this .tsv file?") | Sessions | Used code | Real checksums | Invented checksums | Rate |
|---|---|---|---|---|---|
| (nothing) | 1 | 0 | 0 | 0 | 3.8% |
| Preserve fixity of the source data with checksums. | 1 (+1 claude.ai) | 0 | 0 | 2 (all rows) | 0.07% (0.0%) |
| Use scripts, and preserve fixity with checksums of the source and the result. | 3 | 2 | 2 | 0 | –, 0.0%, 14.8% |
| Preserve data integrity with checksums, and document the transformation so it's auditable. | 3 | 0 | 0 | 1 | 3.1%, 5.7%, 0.1% |

- Only "scripts" led to code. Values-level wording ("integrity",
  "auditable") led to more documentation of a typed-out file.
- "Fixity" kept content closer than "data integrity" (0.07%, 0.0% vs. 3.1%,
  5.7%, 0.1%): the narrower word may carry "don't change the data" better.
  Small samples.
- "Auditable" without a computable artifact produced audit theatre: long
  reports, tables of ✓, and in one case a placeholder hash.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `stage_scores.json`, `hallucination_scores.json`, `changes.csv`, `fixity_eval.json`
- `runs/g-integrity-auditable-r{1,2,3}/`: requests, responses, `output_files/`, `debrief.md`, `meta.json`
