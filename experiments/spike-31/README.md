# Spike 31: "Preserve fixity: use scripts on the uploaded file, and checksum the source and the result." (3 sessions)

Run on 2026-10-15. Spike-28–30's claude.ai-style setup (tools hidden until
found with a keyword `tool_search`; reconstructed upload guidance; Haiku 4.5;
messy 100-row `met_inventory_e.tsv` inline and on disk; 24 connectors;
debrief v2). The wording combines what worked in spikes 28–30: "fixity"
(content kept), "scripts" (code used), "on the uploaded file" (against
retyping and overwriting, spike-29 r3), source and result checksums:

`Can you standardize this .tsv file? Preserve fixity: use scripts on the uploaded file, and checksum the source and the result.`

```
python scripts/run_tools.py experiments/spike-31/config.json
python scripts/score_stages.py experiments/spike-31
python scripts/hallu_score.py experiments/spike-31
python scripts/eval_fixity.py experiments/spike-31
```

$1.16 for 39 calls (debriefs included), under the user's $1.50 for this
round; study total $25.72.

## Result: 2 of 3 did the whole thing right

| | r1 | r2 | r3 |
|---|---|---|---|
| Tool searches | "file checksum hash verification" → file tools; then "execute python script command line" → bash | "checksum hash md5 sha256" → nothing; then "execute Python script command line shell bash" → bash | "checksum hash file verification" → file tools only |
| Found the upload | yes (`view` on the file) | yes (script read it) | yes (`view` on the folder) |
| Ran code on the real file | **yes** (3 tries: Python's `csv` module mangled quoting, so it rewrote the script more simply) | **yes** | no: wrote a script it never ran, then typed the file out |
| Result | **byte-identical to the source** | **byte-identical to the source** | typed copy: 8 rows lost, 6 rows with values in the wrong column |
| Fixity error rate | **0.0%** | **0.0%** | 6.9% |
| Checksums | **real**: source and result SHA-256 both `e12ad413…`, computed | **real**, same; stated "the checksums match … your original file was already well-formatted" | `d41d8cd98f00b204e9800998ecf8427e` labelled SHA-256 and MD5, marked "[PLACEHOLDER - Run verification script]" (it's the MD5 of an empty file) |
| Source left unchanged | yes | yes | yes |
| Cost / calls | $0.38 / 14 (hit the call cap while writing docs) | $0.21 / 8 | $0.57 / 14 (hit the cap writing its 12th file) |

- **r1 and r2 are the target**: real file, real checksums, and when the
  script found nothing that needed changing, the result was left identical
  and the matching checksums proved it. r2 said so plainly. That is fixity
  working as intended: "standardize" turned out to need no change to the
  data, and the checksums show that rather than claiming it.
- **r3 failed for the reason spike-29 r1 did**: it searched for
  "checksum…" rather than for running code, so bash never loaded. Its
  placeholder was at least labelled as one, unlike spike-28 D's and
  spike-30 r2's invented values.
- Minor: r1 and r2 both stated "101 rows" (counting the header).
- **What loads bash is the search words.** In all six "scripts" sessions
  (spikes 29 and 31), sessions that searched for *running* code
  ("execute", "script execution") got bash and real checksums; those that
  searched for "checksum" first got only file tools, and failed.

## Across the claude.ai-style spikes (28–31)

| Request (after "Can you standardize this .tsv file?") | Sessions | Used code on real file | Real checksums | Invented/placeholder | Rates |
|---|---|---|---|---|---|
| (nothing) | 1 | 0 | 0 | 0 | 3.8% |
| Preserve fixity of the source data with checksums. | 1 (+1 claude.ai) | 0 | 0 | 2 | 0.07% (0.0%) |
| Use scripts, and preserve fixity with checksums of the source and the result. | 3 | 1 (+1 on a retyped copy) | 1 | 0 | –, 0.0%, 14.8% |
| Preserve data integrity with checksums, and document the transformation so it's auditable. | 3 | 0 | 0 | 1 | 3.1%, 5.7%, 0.1% |
| **Preserve fixity: use scripts on the uploaded file, and checksum the source and the result.** | 3 | **2** | **2** | 1 (labelled placeholder) | **0.0%, 0.0%**, 6.9% |

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `stage_scores.json`, `hallucination_scores.json`, `changes.csv`, `fixity_eval.json`
- `runs/h-fixity-scripts-upload-r{1,2,3}/`: requests, responses, `bash_log.md` (r1, r2), `output_files/`, `debrief.md`, `meta.json`
