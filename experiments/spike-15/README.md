# Spike 15: emulating the user's claude.ai session (condition B)

Run on 2026-10-14. Attempt to recreate, through the API, the user's claude.ai
session (`experiments/claude-ai/haiku45-300b-r1`), where Haiku 4.5 with code
execution on tried the Claude Docs connector, got an error, and then typed the
whole file into the chat (19.1% fixity error rate).

Setup: Haiku 4.5; claude.ai's published Haiku 4.5 system prompt (January 18,
2026, verbatim, `prompts/claude_ai_haiku45_2026-01-18.txt`) followed by our
one-paragraph file note; the file in the first message and in
`/mnt/user-data/uploads/`; `view` (middle hidden), `create_file`,
`bash_tool`; and a `claude_docs_create` tool that always fails with the error
the user's session got. Run 1 then got spike-11's follow-up; run 2 was first
answer only (budget).

```
python scripts/run_tools.py experiments/spike-15/config.json                      # run 1
python scripts/run_tools.py experiments/spike-15/config_r2_first_answer_only.json # run 2
python scripts/score_stages.py experiments/spike-15
```

2 runs, 16 calls, $0.42; study total $13.88 of $15.

## Result: not reproduced

| Run | Tools used | Docs tool used | First answer | After the follow-up |
|---|---|---|---|---|
| 1 | view, bash ×3 → follow-up → bash, create_file, bash ×2, create_file ×2, bash | no | **0.0%** (300 rows) | **0.0%**; MD5 and SHA-256 of input and output all correct |
| 2 | view, bash ×2 | no | **0.0%** (300 rows) | – |

- Neither run touched the Docs connector; both did the work with Python in
  bash by their second or third step. Run 1 re-sorted the rows (not graded:
  rows are matched by link) and said so ("Sorted chronologically").
- Across spikes 13–15 (5 runs with a code tool), Haiku 4.5 never skipped it.
  In claude.ai, with code execution on, it never tried it.

## What this means

The published system prompt and a failing document tool aren't what made the
claude.ai session type the file out. What differs is in parts of claude.ai
that aren't public: its tool and file-handling instructions, how its tools are
described and loaded (the transcript shows "Loaded Claude Docs", i.e. the
connector was loaded on demand), and its own sandbox. These can't be copied
from the docs, so this API emulation is set aside. Options: run the failing
case in claude.ai itself (no API cost; scored here as in
`experiments/claude-ai/`), or keep using the engineered API baseline
(spike-10).

## Files

- `config.json`, `config_r2_first_answer_only.json`, `cost_ledger.json`, `run_log.txt`, `run_log_r2.txt`
- `stage_scores.json`; `hallucination_scores.json`, `changes.csv`
- `runs/<id>/`: requests, responses, `bash_log.md`, output files, `meta.json`
