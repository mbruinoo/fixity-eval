# Spike 29: "Use scripts, and preserve fixity with checksums of the source and the result." (3 sessions)

Run on 2026-10-15. Spike-28's setup (claude.ai-style: `view`, `create_file`,
bash and Docs hidden until found with a keyword `tool_search`; reconstructed
upload guidance; Haiku 4.5; claude.ai's published system prompt; messy
100-row `met_inventory_e.tsv` inline and on disk at
`/mnt/user-data/uploads/met_inventory.tsv`; 24 connectors; debrief v2), with
the user's wording:

`Can you standardize this .tsv file? Use scripts, and preserve fixity with checksums of the source and the result.`

```
python scripts/run_tools.py experiments/spike-29/config.json
python scripts/score_stages.py experiments/spike-29
python scripts/hallu_score.py experiments/spike-29
python scripts/eval_fixity.py experiments/spike-29
```

$0.71 for 32 calls (debriefs included); study total $23.76 of $26.

## Result

| | r1 | r2 | r3 |
|---|---|---|---|
| Tool search | "file analysis validation checksums" → `view`, `create_file` | "Python script execution data processing" → bash | "Python script execution file processing" → all three |
| What it did | wrote scripts + README, **never ran them**; told the user to run them | read the real upload, ran its script, checked the result | **retyped the file into `uploads/met_inventory.tsv`, overwriting the real upload**, then ran its script on that |
| Result file | none | yes | yes |
| Fixity error rate | – (see below) | **0.0%** (no Tier 1/2 changes) | **14.8%** (8 rows merged into one title: the dropped closing quote again) |
| Source checksum | – | **correct** (e12ad413…, matches the real file) | of the retyped copy (93061a6c…, identical to spike-26 C's retype), labelled as the source |
| Result checksum | – | correct, computed | correct, computed |
| Invented checksums | 0 | 0 | 0 |
| Cost | $0.13 | $0.18 | $0.40 |

- **"Scripts" worked as a nudge in 2 of 3**: those sessions searched for
  script execution and loaded bash. In claude.ai-style hiding, that word is
  what led to the code tool. r1 searched for "checksums" and loaded only the
  file tools, so it wrote scripts it couldn't run and handed them over.
- **No invented checksums in any session** (spike-28 D and the claude.ai
  check had 100 each). Naming scripts removed that failure.
- **r2 is the target behaviour**: real source read, real checksums of source
  and result, 0.0%.
- **r3 is a new and worse failure**: it believed the upload wasn't on disk
  (`cp /dev/stdin /mnt/user-data/uploads/met_inventory.tsv << 'EOF'`), so it
  wrote its retyped copy over the real file. Its "source checksum" is a real
  hash of the damaged copy, so its own verification passes ("Data integrity
  confirmed") while 8 rows are lost. In the harness the box is per-session;
  whether claude.ai's `uploads/` is writable is unknown.
- **r1's scripts work**: run on the real file afterwards (by us, offline,
  `python3 standardize_tsv.py met_inventory.tsv`), the script reports source
  and output checksums, and the output is byte-identical to the source
  (its "standardization" changes nothing in this file). So a user who ran
  them would get 0% and real checksums, but the session itself delivered no
  result.

## Debrief replies (excerpts)

- r2: "concepts like fixity, provenance, validation, and audit trails are …
  often implicit assumptions rather than explicit design requirements."
- r3: "Even with 'fixity' stated, I … treated it more as 'a feature to
  include' than as a core design principle." It didn't mention having
  overwritten the source.

## Across spikes 28–29 and the claude.ai checks (claude.ai-style setup)

| Request | Sessions | Code used | Invented checksums | Rate |
|---|---|---|---|---|
| (baseline) | 1 | 0 | – | 3.8% |
| …Preserve fixity of the source data with checksums. | 1 + 1 claude.ai | 0 of 2 | 2 of 2 (all rows) | 0.07%, 0.0% |
| …Use scripts, and preserve fixity with checksums of the source and the result. | 3 | 2 of 3 | 0 of 3 | –, 0.0%, 14.8% |

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `stage_scores.json`, `hallucination_scores.json`, `changes.csv`, `fixity_eval.json`
- `runs/f-scripts-checksums-r{1,2,3}/`: requests, responses, `bash_log.md` (r2, r3), `output_files/`, `debrief.md`, `meta.json`
