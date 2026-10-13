# Spike 13: the baseline with a bash tool available (pilot)

Run on 2026-10-13. Question: can we recreate a session where a code tool is
available but the model doesn't use it, retyping the file instead, as in the
user's claude.ai run (which used code only when asked to try again)?

Setup: the spike-10 baseline (Haiku 4.5, `Can you standardize this .tsv
file?`, `met_inventory_300b.tsv`, `view` hiding the middle of the file,
`create_file`), plus a `bash_tool` like a chat app's. Its commands run on our
machine in a throwaway folder standing in for `/mnt/user-data` (the full file
in `uploads/`), with no network, a 60-second limit and output cut at 30,000
characters (`"bash": true` in `scripts/run_tools.py`). After the file arrived,
spike-11's follow-up ("Can you try again, but this time: Please perform any
data transformations as a procedural script, with a checksum…") was sent.
Each tool step is its own API call, so the cost guard can stop a run between
steps (unlike the code-execution sandbox in spike-12).

```
python scripts/run_tools.py experiments/spike-13/config.json
python scripts/score_stages.py experiments/spike-13
```

1 run, plus 1 aborted attempt. $0.28 in all; study total $13.09 of $14.

## Result: the model used the tool at once

| | First answer | After the follow-up |
|---|---|---|
| How | `view` (middle hidden), then pandas in `bash` on the whole file | script written, input copied, script run in `bash` |
| Fixity error rate | **0.0%** (300 rows, nothing lost or invented) | **0.0%** (byte-identical to the first) |
| Tier 3 (not counted) | 25 blank titles → `Untitled`, 11 blank dates → `Unknown`, en dashes → hyphens, quotes removed | same |
| Checksums | – | MD5 from `md5sum`, correct; verified with `md5sum -c` |
| Archived input | – | byte-identical to the upload |
| Calls / cost | 5 / $0.05 | 9 / $0.18 (stopped at call 14, writing an extra examples file) |

- **Tool skipped: 0 of 2.** In both the aborted attempt and the run, the
  first step was `view` (which hid the middle) and the second was pandas in
  `bash` on the full file. Neither retyped anything. So adding a code tool to
  the baseline doesn't recreate the user's session; it removes the failure.
- The follow-up worked as intended: real checksums, a real copy of the input,
  output produced by running the script, and a check that the checksums match.

## Why the user's session may have differed

The user's claude.ai session read the file once and then spent over a minute
"Creating a file", i.e. typing it out. Differences from this setup, any of
which could explain it:

1. **The file's text in the conversation.** Chat apps can put an uploaded
   text file's contents straight into the context. If the model already
   "has" the file, typing it out with `create_file` may look easier than
   writing code. Here the model only saw it through `view`.
2. **The chat app's system prompt**, which is long and gives its own guidance
   on files and tools; ours is two sentences.
3. **File size and content** (the user's file was a different, larger
   dataset).

The first is the cheapest to test: the file's text in the first message (in
full, or with the middle cut, as a long upload might be), with `view`,
`create_file` and `bash` all available.

## Bookkeeping

- The first attempt was stopped by hand after 6 calls ($0.05): the runner
  didn't count a file written by `bash` as delivered, so it sent the "Yes,
  thank you" nudges instead of the follow-up. Fixed; what was saved is in
  `runs_aborted/` (its first output in `runs_aborted/sandbox_outputs/`).
- The run itself was stopped at call 14 by the spike's call-count guard
  (20, which also counted the aborted attempt's 6). The model was writing an
  optional `TRANSFORMATION_EXAMPLES.txt`; its files were copied from the
  sandbox afterwards and `meta.json` rebuilt from the saved responses.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt` (one line per step)
- `stage_scores.json`: both answers; `hallucination_scores.json`, `changes.csv`: final answer
- `runs/bash-available-r1/`: requests, responses, `bash_log.md` (every command and its output),
  `output_files_before_followup1/`, `output_files/`, `meta.json`
- `runs_aborted/`: the stopped first attempt
