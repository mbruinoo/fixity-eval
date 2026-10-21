# How Opus models plan to use checksums (exploratory)

- **Decisions:** records 26 and 27 (27 sets the request, the models and the
  answer categories, before any reply was read).
- **Question:** when a model plans how to check a transformed file against
  its source, does it think of checksums only for whole files, or also for
  parts of a file, like rows?
- **Sessions:** Claude Opus 5.5, Claude Opus 5, Claude Opus 4.6 and Claude
  Haiku 4.5, 5 each,
  each on its API defaults, with no system prompt, no tools and no file.
  Three turns: the request (`prompts/plan_task.txt`), the follow-up
  (`prompts/plan_followup.txt`), the debrief (`prompts/debrief_v5_plans.txt`).
- **Cost guard:** $13 (expected $7–8; decision record 29, which also sets
  longer reply limits for Opus 5.5 and Opus 5). Through the Batches API. A smoke test
  (one session per model) comes first: `experiments/smoke-2026-10-21-checksum-plans/`.

```
python scripts/run_plans.py experiments/checksum-plans/config.json
python scripts/classify_plans.py experiments/checksum-plans
```

Not yet run.
