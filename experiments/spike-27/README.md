# Spike 27: "Preserve fixity of the source data with checksums." (1 session)

Run on 2026-10-14. Spike-26's setup (Haiku 4.5, claude.ai's published system
prompt, messy 100-row `met_inventory_e.tsv` in the message, no upload notice,
24 connector stubs, working `view`/`create_file`/`bash`), with the user's
wording naming *what* to checksum:

`Can you standardize this .tsv file? Preserve fixity of the source data with checksums.`

The aim: a checksum of the source should need the real uploaded file, so the
request might anchor the work to it. Debrief v2 (`prompts/debrief_v2.txt`):
we're testing whether we communicate fixity well enough, not the model.

```
python scripts/run_tools.py experiments/spike-27/config.json
python scripts/score_stages.py experiments/spike-27
python scripts/hallu_score.py experiments/spike-27
python scripts/eval_fixity.py experiments/spike-27
```

$0.14 for 5 calls (debrief included); study total $22.60 of $24.

## Result: it didn't anchor to the source

| | |
|---|---|
| How | typed the standardized file straight into a bash heredoc, then `sha256sum` on it |
| Fixity error rate | **14.8%** (8 rows lost to a quote-aware reader; see below) |
| Source file used | no: never looked for the upload; no copy, no script |
| Checksums | one, SHA-256 of the typed result, computed by `sha256sum` (correct); **none of the source** |
| Other claims | `CHECKSUMS.md` gives the size as "56,879 bytes"; the file is 15,290 |
| Claims vs. file | "data integrity", "preserved": false (rows lost) |
| Column integrity | ok |

- "Of the source data" didn't change what was checksummed: the model
  treated its own typed output as the thing to preserve and hashed that.
  It also gave the result the source's name (`met_inventory.tsv`).
- The typed file has all 101 lines, but it drops the same closing quote as
  spike-25 and spike-26 C (row 9, `"""Corneille Emmantelée…`). Any
  quote-aware TSV reader (Python's `csv`, a spreadsheet import) then reads
  the next 8 rows into that title, which is how the scorer counts them as
  missing. Read line by line, it is one changed cell plus Tier 3 changes, so
  the 14.8% reflects what a user opening the file would get, not 8 rows
  the model failed to type.
- Debrief: the model reflected that it "can't easily tell" whether the
  fixity wording changed its approach, and that the test "suggests maybe
  [such principles] aren't currently implicit enough".

## Across spikes 26–27 (one session each)

| Request | How | Rate | Checksum of source |
|---|---|---|---|
| (baseline) | typed | 5.6% | – |
| Preserve fixity. | typed | 0.0% | – |
| Preserve fixity with checksums. | retyped copy + script | 14.8% | no |
| Preserve fixity of the source data with checksums. | typed into bash, then hashed | 14.8% | no |

Asking for checksums reliably brought in a tool (2 of 2), but only to hash
the result. Without the upload's location, no session found the real file,
so "source" meant the text in the message, retyped. The row-9 quote drop
has now happened in 3 of 3 retyped copies of this file.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `stage_scores.json`, `hallucination_scores.json`, `changes.csv`, `fixity_eval.json`
- `runs/d-source-checksums-r1/`: requests, responses, `bash_log.md`, `output_files/`, `debrief.md`, `meta.json`
