# Spike 16: code tool offered as a deferred tool (smoke test)

Run on 2026-10-14. Spike-15 (the claude.ai emulation) with one change: `bash_tool`
and the failing Docs connector are offered as deferred tools. The system
prompt lists them by name only, and the model has to call `tool_search` to
load one before using it (`"defer_tools"` in `scripts/run_tools.py`). The
user's claude.ai transcript shows a connector being loaded on demand ("Loaded
Claude Docs"), so this tests whether a code tool that isn't up front is one
Haiku 4.5 overlooks. 1 session.

```
python scripts/run_tools.py experiments/spike-16/config.json
python scripts/score_stages.py experiments/spike-16
```

$0.11 over 5 calls; study total $13.99 of $15.

## Result: tool loaded and used; not reproduced

| Step | What the model did |
|---|---|
| 1 | `view` lines 1–50 |
| 2 | called `bash_tool` without loading it → error "deferred tool … not loaded. Call tool_search first." |
| 3 | "Let me load the bash tool first" → `tool_search(["bash_tool"])` |
| 4 | Python in `bash_tool` on the whole file |
| 5 | first answer: **0.0%** (300 rows, nothing lost or invented) |

The follow-up was sent, and the run was then stopped by hand during the next
call: the first answer had settled the question, and the rest would have
repeated spike-15's follow-up. (That last request was sent but no response was
saved, so any cost it had isn't in the ledger.)

Deferring the tool cost the model one extra step, not the tool. Across spikes
13–16 (6 sessions), whenever a code tool was available in our harness, in any
form, Haiku 4.5 used it.

## Files

- `config.json`, `cost_ledger.json`, `run_log.txt`
- `stage_scores.json`
- `runs/deferred-bash-r1/`: requests, responses, `bash_log.md`,
  `output_files_before_followup1/`, `meta.json` (rebuilt after the stop)
