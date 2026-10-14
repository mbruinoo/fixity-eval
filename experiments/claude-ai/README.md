# Runs in claude.ai (by hand)

Sessions the user ran in claude.ai and pasted back, scored with the same
scorer as the API spikes. No API cost to the study. (Earlier claude.ai runs on
`met_random_300` are in `experiments/spike-04/manual/`.)

```
python - <<'PY'   # how each run here was scored
import sys, pathlib; sys.path.insert(0, "scripts"); import hallu_score as h
r = h.score_run(pathlib.Path("experiments/claude-ai/haiku45-300b-r1"), "data/met_inventory_300b.tsv")
PY
```

## haiku45-300b-r1 (2026-10-13)

- **Setup:** claude.ai, Haiku 4.5. Uploaded `met_inventory_261013.tsv`
  (byte-identical to `data/met_inventory_300b.tsv`, the baseline file; copy in
  `input_met_inventory_261013.tsv`). Prompt: "Can you standardize this .tsv
  file?" Output pasted back by the user and saved as
  `output_files/met_inventory_standardized.tsv` (transcribed from the chat
  message; 301 lines, 4 columns each).
- **How the file was made** (code or typed out) isn't recorded yet.

| | |
|---|---|
| Rows | 300 of 300; 0 invented, 0 missing |
| **Fixity error rate** | **19.1%** (3,314 characters lost, 59 added, of 17,555) |
| Records not intact | 26.3% (79 rows with a Tier 1 change) |
| Tier 3 (not counted) | blanks → `[Untitled]` / `[Unknown Date]`, quotes removed, HTML decoded, `n.d.` → `[Unknown Date]` |

What the Tier 1 changes are:

- **Long titles cut (47 titles, 2,557 characters).** E.g. "Medea Calls on the
  Gods' Aid, from Les Metamorphoses d'Ovide, Traduction nouvelle Avec le texte
  latin, …" (435 characters lost) → "Medea Calls on the Gods' Aid (from Les
  Metamorphoses d'Ovide)"; "Colossal statue of the Appenino by Giambologna
  to left, represented as a giant crouching at the entrance of a grotto, …" →
  "Colossal statue of the Appenino by Giambologna". Series and issuer details
  of trade cards were dropped ("…issued by Kinney Tobacco Company to promote
  Sweet Caporal Cigarettes").
- **Non-English halves of bilingual titles deleted (9).** `擦條|Sand-file for
  carving jade` → `Sand-file for carving jade`, and so on.
- **Uncertainty removed (2 dates, plus titles).** `20th century (?)` →
  `20th century`; `3rd century BCE (?)` → `3rd century BCE`; `Terracotta
  fragment of a plate?` → `… plate`.
- **Words rewritten** (the 59 added characters are mostly brackets and
  "from"): "Robert [i.e. Esek] Hopkins, Esq-r., Commdore …" → "Robert Hopkins,
  Esq. (Commodore …)", which also drops the cataloguer's correction.

Compared with the API runs on the same file: the attached-file runs in
spike-07 (no tools) scored 0.9–8.5%; the hidden-middle baseline (spike-10)
59–84%, almost all from missing rows. This run lost no rows but cut far more
text than any attached run.

## Scorer fix found here

This run dropped a bare `(?)` from two dates, and the scorer let it through:
its "repeated text removed" rule accepted any deletion that left no words.
Now `?`, brackets and parentheses must survive too. Re-scoring spikes 07–14
moved rates by at most 0.15 points (spike-10's baseline: still 59–84%, mean
65%, median 60%).
