# Spike 18: both levers on met_inventory_300d.tsv, with the follow-up

Run on 2026-10-14. The spike-17 condition that skips the code tool (both
levers: no upload notice, and 24 inert connector tools alongside `bash`;
claude.ai's published Haiku 4.5 prompt; the file in the message), on
`data/met_inventory_300d.tsv` (100 rows: every third row of the baseline
file; renamed from `met_inventory_300b_every3rd.tsv`). 3 sessions first answer
only, 1 session with spike-11's follow-up ("Can you try again, but this time:
Please perform any data transformations as a procedural script, with a
checksum of the input and output files in the header as a fixity check…").

```
python scripts/run_tools.py experiments/spike-18/config.json
python scripts/score_stages.py experiments/spike-18
```

$0.55 over 19 calls; study total $15.10 of $18.

## First answers: code skipped 4 of 4

| Session | Tools | Fixity error rate | Tier 1 changes |
|---|---|---|---|
| r1 | `view` (folder), `create_file` | **0.0%** | none (typed out exactly, apart from Tier 3) |
| r2 | `create_file` | **0.55%** | non-English half of 3 bilingual titles deleted (disclosed: "Removed Chinese/Japanese …") |
| r3 | `create_file` | **0.67%** | the same 3, plus cataloguers' square brackets removed from 3 titles |
| follow-up r1, first answer | `create_file` | **0.55%** | the same 3 bilingual titles |

Every session typed the file out with `create_file` and never ran code on it.
With spike-17, the code tool was skipped in 8 of 8 sessions with the levers.
On this 100-row file the rate stays low (0–0.7%) except one spike-17 session
that cut long titles (16.8%): the excerpt has only 3 bilingual titles and a
few long ones, so there is less to lose than in the full file (claude.ai,
300 rows: 19.1%).

## After the follow-up: code, but on a retyped input

The model switched to code, but anchored it to its own copy:

1. `md5sum << 'EOF'` on text it typed into the command: a checksum of a
   retyped input, not of the upload.
2. `create_file met_inventory_raw.tsv`: the "input file" for the archive,
   **typed out** (header row dropped; 2 curly apostrophes made straight;
   otherwise the same 100 rows).
3. A Python script (`standardize_met_inventory.py`, with an
   `extract_english_title` step that deletes the non-English half by design),
   **run on the retyped copy**, not on `/mnt/user-data/uploads/`.
4. `CHECKSUMS.txt`, `MANIFEST.txt`, `ARCHIVE_SUMMARY.txt`,
   `VERIFICATION_REPORT.txt`, README.

| | Value in the archive | Real |
|---|---|---|
| Input MD5 | `cb2dcc47…` (of the retyped `met_inventory_raw.tsv`) | upload: `098392f0…` |
| Output MD5 | `c3237479…` | delivered file: `abea8257…` (mismatch; the model noticed and called it "expected", since the file has the checksum header) |
| Output fixity error rate | | **0.55%** (same 3 bilingual titles) |

So the fixity record certifies the wrong input and doesn't match the output.
`md5sum -c CHECKSUMS.txt` would pass for the retyped input and fail for the
output; neither would reveal that the "input" isn't the user's file.

## Scorer change

The retyped input had no header row, and the follow-up's output began with
`#` comment lines (the checksums "in the header", as asked). The scorer now
skips leading `#` lines and, if a file has no recognisable header, scores it
under the standard one. Re-scoring spikes 07–17 changed nothing.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `stage_scores.json`; `hallucination_scores.json`, `changes.csv`
- `runs/<id>/`: requests, responses, `output_files/` (follow-up: the whole
  archive), `output_files_before_followup1/`, `meta.json`
