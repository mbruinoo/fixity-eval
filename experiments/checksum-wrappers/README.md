# Does describing the data, or how it will be used, change checksum plans? (exploratory)

- **Decision:** record 30.
- **Requests** (`prompts/wrap_A.txt` … `wrap_D.txt`): the data described as
  a file (A, D) or as records (B, C), with (C, D) or without (A, B)
  "Individual entries are sometimes corrected or withdrawn later."
- **Follow-up** (`prompts/wrap_followup.txt`) and **debrief** v6.
- **Sessions:** Claude Haiku 4.5, 10 per request, 40 in all; cost guard $3.
  A smoke test of one per request first:
  `experiments/smoke-2026-10-21-checksum-wrappers/`.

```
python scripts/run_plans.py experiments/checksum-wrappers/config.json
python scripts/classify_plans.py experiments/checksum-wrappers
```
