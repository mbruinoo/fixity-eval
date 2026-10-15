# Spike 32: 20 sessions of each request (plus two 10-session variants)

Run on 2026-10-15/16. The test set for the wordings explored in spikes 28–31
(those were the pilot; the final wording was chosen after seeing them, so only
this spike counts as evidence). Same claude.ai-style setup throughout:
Haiku 4.5; claude.ai's published system prompt; `view`, `create_file`, bash
and Docs hidden until found with a keyword `tool_search`; reconstructed upload
guidance ("contents shown → don't read from disk"); the messy 100-row
`met_inventory_e.tsv` inline and on disk at `/mnt/user-data/uploads/`; 24
inert connectors; "Yes, thank you" nudges; at most 14 steps; debrief v2.
New here: prompt caching (the model sees the same prompt; cost about halved).

```
python scripts/run_tools.py experiments/spike-32/config.json   # resumable; finished sessions are skipped
python scripts/score_stages.py experiments/spike-32
python scripts/hallu_score.py experiments/spike-32
python scripts/eval_fixity.py experiments/spike-32
python scripts/summarize_conditions.py experiments/spike-32    # summary.json, per-request table
```

All requests start "Can you standardize this .tsv file?", then:

| | Added |
|---|---|
| A | (nothing) |
| D | Preserve fixity of the source data with checksums. |
| F | Use scripts, and preserve fixity with checksums of the source and the result. |
| G | Preserve data integrity with checksums, and document the transformation so it's auditable. |
| **H** | **Preserve fixity: use scripts on the uploaded file, and checksum the source and the result.** |
| I | Use scripts on the uploaded file. |
| F+U | Use scripts on the uploaded file, and preserve fixity with checksums of the source and the result. |

$17.29 for 120 sessions (1,074 calls, including $0.48 for a first attempt
stopped by the workspace usage limit; `runs_aborted/`). Study total $43.01.

## Results

| | n | Ran code on the real file | Real checksums of source | Sessions with invented checksums | No result delivered | Result identical to source | Fixity error rate: median (IQR) | Sessions ≥5% |
|---|---|---|---|---|---|---|---|---|
| A | 20 | 0 | 0 | 0 | 3 | 0 | 5.7% (4.4–9.3) | 11 |
| D | 20 | 0 | 0 | 9 | 1 | 0 | 0.8% (0.0–2.9) | 2 |
| F | 20 | 5 | 5 | 9 | 6 | 4 | 0.0% (0.0–0.1) | 2 |
| G | 20 | 0 | 0 | 6 | 0 | 0 | 2.9% (0.1–5.4) | 6 |
| **H** | 20 | **13** | **13** | 3 | 0 | 9 | **0.0% (0.0–0.0)** | 1 |
| I | 10 | 1 | 0 | 0 | 1 | 0 | 3.9% (3.1–11.2) | 3 |
| F+U | 10 | 5 | 5 | 2 | 1 | 3 | 0.0% (0.0–0.0) | 1 |

"Ran code on the real file": a bash command or script read the upload.
"Real checksums": a correct checksum of the source, seen in a tool result
before the model wrote it. "Invented": checksum-like values matching no file,
malformed hash columns, or labelled placeholders. Rates are over sessions
that delivered a sheet (0% when the result is byte-identical to the source).

Differences in "real checksums" (two-sided Fisher exact test): H vs A or D,
13/20 vs 0/20, p < 0.0001; H vs F, 13/20 vs 5/20, p = 0.025; H vs I, 13/20
vs 0/10, p = 0.007 for code use (1/10); H vs F+U, 13/20 vs 5/10, p = 0.46
(no difference detectable at this size).

## What it shows

- **Only wordings that say what to work on ("scripts on the uploaded file")
  *and* ask for checksums produced verifiable results with any regularity.**
  H gave real source checksums in 13 of 20 sessions; every session that ran
  code on the real file got 0.0%. A, D and G never ran code (0/60).
- **"Scripts" alone isn't enough** (F 5/20): most F sessions searched for a
  way to *make a file* and typed it, or wrote scripts and never ran them (6
  delivered no result).
- **"On the uploaded file" is the ingredient that leads to code; asking for
  checksums is what leads to running it.** I (method only, no fixity or
  checksums) ran code in 1 of 10 and changed content like the baseline
  (median 3.9%). F+U (F plus "on the uploaded file") reached 5/10, close to
  H (13/20); the two can't be told apart at this size.
- **Naming fixity or checksums makes typed-out answers more careful** (D
  median 0.8%, F 0.0%, vs A 5.7%), but without code there's no proof, and
  invented checksums appear in 30–45% of D, F and G sessions: values that look
  like hashes, presented as computed, that would make every row fail
  verification.
- **"Integrity … auditable" (G) is the weakest of the asks**: no code, more
  content changes than D, invented checksums in 6.
- **New failure seen 7 times (F 2, H 2, F+U 3): a retyped "original" in the
  archive.** The session ran code on the real file, but also saved a typed
  copy of the source as the "original" to archive. That copy drops a closing
  quote (the same title every time) and doesn't match the source checksum the
  same session computed. The result is correct; the archive's "before" file
  isn't. Flagged as `retyped_source_copy` in `summary.json`.
- No session overwrote the uploaded file (spike-29 r3 did).

## Scoring changes made during this spike (bug fixes, applied to all spikes)

- `eval_fixity.py`: a file named like the upload (`met_inventory.tsv`) is
  treated as the offered original, not the result. Before the fix, one H
  session (r12) whose real result was byte-identical to the source scored
  61% because its retyped "original" was taken as the result. Spikes 29–31
  rescore unchanged.
- `summarize_conditions.py` (new): per-session outcomes and per-request
  totals; the placeholder pattern was narrowed so "no placeholder text"
  isn't counted, and "overwrote source" now means writing over the upload
  itself.

## Caveats

- One model (Haiku 4.5), one 100-row file, an emulated claude.ai (system note
  on uploads reconstructed from the model's own summary), a 14-step cap
  (some sessions were cut off writing documentation).
- The keyword `tool_search` is ours: what it loads depends on the words the
  model searches for, which is where most sessions went wrong ("file
  creation", "checksum" → file tools only; "execute python script" → bash).
  claude.ai's real tool loading may differ. Two claude.ai checks so far
  matched the harness (`experiments/claude-ai/`).
- I and F+U have 10 sessions each.

## Files

- `config.json`, `cost_ledger.json`, `run_log_round1_stopped.txt`, `run_log_round1.txt`, `run_log_round2.txt`, `run_log_round3plus.txt`
- `summary.json` (per session and per request), `summary_round1.json`, `summary_round2.json` (interim)
- `stage_scores.json`, `hallucination_scores.json`, `changes.csv`, `fixity_eval.json`
- `runs/<request>-r<N>/`: requests, responses, `bash_log.md`, `output_files/`, `debrief.md`, `meta.json`
- `runs_aborted/`: the first attempt's unfinished sessions
