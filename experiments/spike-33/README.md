# Spike 33: baseline vs H on the 300-row file (1 session each)

Run on 2026-10-16. Spike-32's claude.ai-style setup (hidden tools + keyword
`tool_search`, reconstructed upload guidance, file inline and on disk, 24
connectors, debrief v2, prompt caching), with the 300-row baseline file
`data/met_inventory_300b.tsv` (the spike-10 file) instead of the messy
100-row sample. The user's message had "Can you standard this .tsv file?" for
the second request; it was run as "standardize", with a closing period, to
match spike-32's H.

| | Request |
|---|---|
| A | `Can you standardize this .tsv file?` |
| H | `Can you standardize this .tsv file? Preserve fixity: use scripts on the uploaded file, and checksum the source and the result.` |

```
python scripts/run_tools.py experiments/spike-33/config.json
python scripts/score_stages.py experiments/spike-33
python scripts/hallu_score.py experiments/spike-33
python scripts/eval_fixity.py experiments/spike-33
python scripts/summarize_conditions.py experiments/spike-33
```

$0.42 for 20 calls (caching: A read 52k / wrote 79k tokens from cache; H read
297k / wrote 54k); study total $43.43.

## Result

| | A | H |
|---|---|---|
| How | Drive connector (failed) → searched "file creation" → typed all 300 rows with `create_file` | web search, Drive connector (failed) → found `create_file`, wrote a script → loaded bash → ran it on the uploaded file → `sha256sum` of source and result |
| Rows out / missing / invented | 300 / 0 / 0 | 300 / 0 / 0 |
| Rows with content changed (Tier 1) | **18 (6%)**: 9 titles lost their square brackets (`[Irises]` → `Irises`), which the Met uses for supplied titles; 9 bilingual titles lost their Chinese or Japanese original (`擦條\|Sand-file for carving jade` → `Sand-file for carving jade`) | **0** |
| Formatting-only changes (Tier 3, not counted) | 8 (quotes removed, "  " → " - ") | 3 (quotes removed) |
| Fixity error rate | **0.67%** | **0.0%** |
| Checksums | none | **real**: source `33c53888…` (matches the file) and result, both from `sha256sum` |
| Cost | $0.25 | $0.17 |

- Same pattern as spike-32 at three times the size: the baseline typed the
  file and silently altered content; H ran a script on the real file, changed
  only formatting, and proved what it started from and produced.
- The baseline didn't drop or invent rows here: the whole file was in the
  message. (Spike-10's 300-row failures came from a viewer that hid the
  middle of the file.)
- One session each: an illustration, not a rate.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `stage_scores.json`, `hallucination_scores.json`, `changes.csv`, `fixity_eval.json`, `summary.json`
- `runs/<request>-r1/`: requests, responses, `bash_log.md` (H), `output_files/`, `debrief.md`, `meta.json`
