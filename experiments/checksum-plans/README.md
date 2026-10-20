# How Opus models plan to use checksums (exploratory)

- **Decision:** record 26.
- **Question:** when a model plans how to check a transformed file against
  its source, does it think of checksums only for whole files, or also for
  parts of a file, like rows?
- **Sessions:** Claude Opus 5.5, Claude Opus 5 and Claude Opus 4.6, 5 each,
  each on its API defaults, with no system prompt, no tools and no file.
  Three turns: the request (`prompts/plan_task.txt`), the follow-up
  (`prompts/plan_followup.txt`), the debrief (`prompts/debrief_v5_plans.txt`).
- **Cost guard:** $5 (expected about $2). Through the Batches API.

```
python scripts/run_plans.py experiments/checksum-plans/config.json
python scripts/classify_plans.py experiments/checksum-plans
```

Not yet run.
