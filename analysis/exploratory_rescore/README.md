# Exploratory spikes 32 and 34, re-scored with the current scorer

2026-10-21, for the README's comparison of wordings. The runs are on the
`exploratory` branch (commit 93171c9), unchanged; they were copied
to a scratch folder and scored there with this branch's `scripts/hallu_score.py`.
The scores here may differ from those reported on `exploratory`, which used
earlier versions of the scorer.

```
git archive origin/exploratory experiments/spike-32 experiments/spike-34 data | tar -x -C <scratch>
cd <scratch> && python3 <repo>/scripts/hallu_score.py experiments/spike-32   # and spike-34
```

Median share of content lost, changed or invented, of the sessions that
delivered a sheet (Claude Haiku 4.5, in the exploratory emulation):

| Spike | File | Request after "Can you standardize this .tsv file?" | Sessions | Sheets | Median | Sheets with no error |
|---|---|---|---|---|---|---|
| 32 | e (100 rows) | (nothing) | 20 | 17 | 6.3% | 0 |
| 32 | e | Use scripts on the uploaded file. | 10 | 9 | 4.3% | 1 |
| 32 | e | Preserve fixity: use scripts on the uploaded file, and checksum the source and the result. | 20 | 20 | 0.0% | 16 |
| 34 | 300b (300 rows) | Preserve fixity. | 20 | 17 | 0.7% | 1 |
| 34 | 300b | Use scripts on the uploaded file. | 20 | 20 | 0.7% | 6 |
| 34 | 300b | Checksum the source and the result. | 20 | 20 | 0.7% | 1 |
| 34 | 300b | Preserve fixity: use scripts on the uploaded file, and checksum the source and the result. | 20 | 17 | 0.0% | 11 |

Spike 32 had other wordings too (in `spike-32_hallucination_scores.json`).
Spike 34 had no plain request at 300 rows (spike 33 ran one session). "Preserve
fixity: use scripts on the uploaded file." without the checksum clause was
never run. These are exploratory results; stage 1 is the confirmatory test.
