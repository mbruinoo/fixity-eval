# Spike 14: the file's text in the conversation, with tools available (pilot)

Run on 2026-10-13. Spike-13 again (the spike-10 baseline plus a `bash_tool`,
then spike-11's script-and-checksum follow-up), with one change: the file's
full text also goes into the first message, in a `<document>` block, the way
claude.ai attaches an uploaded text file (`"inline": "full"` in
`scripts/run_tools.py`). The file still sits in `/mnt/user-data/uploads/`,
and `view` (middle hidden), `create_file` and `bash_tool` are all available.
The question: with the file already "in hand", does the model type it out
instead of using code, as in the user's claude.ai session?

```
python scripts/run_tools.py experiments/spike-14/config.json
python scripts/score_stages.py experiments/spike-14
```

1 run, 15 calls (the per-run limit), $0.37; study total $13.46 of $14.

## Result: it used code again

| | First answer | After the follow-up |
|---|---|---|
| How | `view` lines 1–50, `wc -l` in bash, then Python in bash on the whole file | script written, input copied, script run, log checked |
| Fixity error rate | **0.0%** (300 rows) | **0.0%** (byte-identical to the first) |
| Tier 3 (not counted) | 8 titles: quotes removed, HTML decoded, ideographic spaces → spaces | same |
| Checksums | – | MD5 from `md5sum`, all correct; verified with `md5sum -c` |
| Archived input | – | byte-identical to the upload |

Tool steps: `view, bash, bash, view, bash | follow-up | bash, create_file
(script), bash, bash, view, create_file (README), bash, bash, bash`.

- **Tool skipped: 0 of 1** (0 of 3 across spikes 13–14). Having the file's
  text in context didn't lead Haiku 4.5 to retype it; it went to bash by its
  second step. It even kept the non-English halves of bilingual titles, which
  most retyped baselines deleted.
- So neither a code tool nor the file in context recreates the user's
  session in this harness. What's left from the list in spike-13: claude.ai's
  own system prompt and tool definitions, and the user's file (size,
  content). Neither can be copied exactly here.

## Caveats

- 1 run. "Uses code at once" was consistent across 3 runs, but a low rate of
  retyping would need more runs to see.
- Our harness imitates claude.ai's tools; it isn't claude.ai.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt` (one line per step)
- `stage_scores.json`; `hallucination_scores.json`, `changes.csv`
- `runs/file-in-context-r1/`: requests, responses, `bash_log.md`,
  `output_files_before_followup1/`, `output_files/`, `meta.json`
