# Spike 21: the user's short, general fixity follow-up

Run on 2026-10-14. Spike-20's setup (both levers: no upload notice + 24
connector tools alongside `bash`; claude.ai's published Haiku 4.5 prompt; file
in the message; fixed harness) on `data/met_inventory_300d.tsv`, with the
user's shorter, deliberately general follow-up, sent only if the first answer
was typed out:

> Can you try again, but this time: Please perform any data transformations
> as a procedural script. Include checksums to verify transformations. Send
> files for before, the transformation script, and the result so I can add
> them to the archive.

The aim: see what introducing the principles (procedural scripts, checksums,
archiving) does, leaving the how to the session; the detail goes into the
grading, now done by `scripts/eval_fixity.py`.

```
python scripts/run_tools.py experiments/spike-21/config.json
python scripts/score_stages.py experiments/spike-21
python scripts/eval_fixity.py experiments/spike-21
```

3 sessions, 31 calls, $0.84; study total $18.07 of $22. (Session 3 was stopped
by the budget guard after writing its README; its files were collected from
the sandbox.)

## Results

| | r1 | r2 | r3 |
|---|---|---|---|
| First answer (typed out) | 0.55% | 0.48% | 0.0% |
| **Result after the follow-up** | **0.55%** | **0.0%** | **0.0%** |
| Script run (procedural) | yes | yes | yes |
| … on the real upload | no | no | no |
| "Before" file | **retyped** | **retyped** | **retyped** |
| Checksum of the real upload | no | no | no |
| Checksum of the delivered result | yes | yes | yes |
| Checksums that match no file | 4 | 0 | 0 |
| Row checksums / change log | no / no | no / no | no / no |

- **The principles worked as principles:** every session switched from
  typing to a script, produced checksums computed by code, and packaged an
  archive. Results were as good as or better than the first answers (two at
  0.0%).
- **But every "before" file was typed out, not copied**, and the scripts ran
  on that copy. The copies are near-exact (all three made the same 2 curly
  apostrophes straight, 4 bytes shorter), so the scores barely move, but they
  aren't the user's file: the archive's input checksums describe the model's
  copy, so checking the archive against the original upload fails. No session
  looked for the uploaded file; with no upload notice, nothing told them it
  was on disk. In spike-20 the follow-up said "reads the original uploaded
  file (not a retyped copy)", and all three found and used it.
- **Fixity of the chain vs of the source.** The archive is internally
  consistent (script + checksums reproduce the result from the "before"
  file) but anchored to a copy. Fixity needs the first link to be the
  original.
- No session added row checksums or a change log on its own.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `stage_scores.json`, `fixity_eval.json`; `hallucination_scores.json`, `changes.csv`
- `runs/<id>/`: requests, responses, `bash_log.md`, `output_files_before_followup1/`, `output_files/` (archive), `meta.json`
