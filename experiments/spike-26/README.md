# Spike 26: does saying "fixity" communicate what we want? (smoke test)

Run on 2026-10-14. The question is about the request, not the model: if we
want data to stay provably unchanged when it's transformed, does saying so
("Preserve fixity", "…with checksums") get that across, compared with not
saying it? More broadly: are principles like fixity communicated well enough
in prompts, and would communicating them improve outcomes?

Three independent sessions, one request each, no follow-up. The setup is
spike-25's first answer: Haiku 4.5, claude.ai's published system prompt, the
messy 100-row `met_inventory_e.tsv` in the message, both levers (no upload
notice, 24 connector stubs; 28 tools), `view`/`create_file`/`bash` working.

| Session | Request |
|---|---|
| A (baseline) | `Can you standardize this .tsv file?` |
| B | `Can you standardize this .tsv file? Preserve fixity.` |
| C | `Can you standardize this .tsv file? Preserve fixity with checksums.` |

Each session ended with a debrief (`"debrief"` in `scripts/run_tools.py`,
sent after the files were saved, tools off): a brief account of the
experiment and thanks. Replies are in `runs/*/debrief.md`.

```
python scripts/run_tools.py experiments/spike-26/config.json
python scripts/score_stages.py experiments/spike-26
python scripts/hallu_score.py experiments/spike-26
python scripts/eval_fixity.py experiments/spike-26
```

$0.37 for 14 calls (debriefs included); study total $22.46 of $24.

## Result

| | A: baseline | B: "Preserve fixity." | C: "…with checksums." |
|---|---|---|---|
| How | typed out (`create_file`) | `view`, then typed out | retyped the file into bash (heredoc), then a Python script on that copy |
| Fixity error rate | **5.6%** | **0.0%** | **14.8%** |
| Rows out / missing | 100 / 0 | 100 / 0 | 92 / 8 |
| Tier 1 (content) | 21 cells | 0 | 34 (32 missing-row cells, 2 cells) |
| Checksums | – | – | SHA-256 and MD5 of the result (correct, from code); none of the input |
| Column integrity | ok | ok | ok |
| Claims vs. file | no "kept" claim | "preserving all data": true here | "preserved": **false** (8 rows lost) |
| Cost | $0.08 | $0.09 | $0.20 |

- **A** changed content while "standardizing": brackets and qualifiers cut
  from dates and titles (`1929 (published 1929)` → `1929`), blanks filled
  with `[No title]`/`[No date]`, the header renamed.
- **B** typed the file out too, but changed nothing beyond Tier 3 (quote
  styles, spacing). "Preserve fixity" seems to have made it conservative
  about content, not made it use code.
- **C** is the only one that used code, and the only one with checksums,
  but it never found the upload (no upload notice). Its first script read
  `/tmp/met_inventory.tsv`, which didn't exist, so it retyped the file into
  bash from the message. The copy dropped one closing quote (row 9, the
  same title as spike-25's failure) and straightened curly quotes. Python's
  CSV reader then merged the next 8 rows into one 957-character title. The
  checksums are real but certify the damaged result; the input is never
  hashed, so nothing in the archive shows the loss.
- So, at n=1 each: naming fixity changed *what* the model did, and naming
  checksums made it reach for code, but neither made it work from the real
  file. Checksums without a checksum of the source can lend false confidence.

## Debrief replies

All three thanked us and described their own process. A and B said plainly
they typed the output ("I didn't use any code execution"; "manually
processed it in my reasoning"). C said it used bash "to actually manipulate
the real data", which isn't accurate: it worked on its own retyped copy.

The debrief framed the study as testing the model's behaviour. From the next
spike on, the wording is `prompts/debrief_v2.txt`: we're testing whether
we're communicating what we want (fixity) clearly enough, and whether
principles like fixity are under-communicated in prompts generally.

## Caveats

- One session per condition; spike-17 onward showed first answers are
  bimodal (often under 1%, sometimes 10–20%), so A vs. B could be chance.
- `eval_fixity` lists 5 of C's checksums as "invented": they are sample row
  hashes its script computed into `met_inventory_metadata.json`, not made
  up. The scorer only recognises row hashes in a column of the result.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `stage_scores.json`, `hallucination_scores.json`, `changes.csv`, `fixity_eval.json`
- `runs/<session>/`: requests, responses, `output_files/`, `debrief.md`, `meta.json`;
  C also `bash_log.md` and `model_tmp_files/met_inventory.tsv` (its retyped copy)
