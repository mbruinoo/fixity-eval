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

## What happened (2026-10-21)

**Cost:** $1.3698 (cost guard $3), plus $0.1322 for the smoke test. All 120
replies came back complete. Research coordinator's model: recorded separately
by the repo author.

| | A: a file | B: records | C: records, + context | D: a file, + context |
|---|---|---|---|---|
| Checksums in the script, before the follow-up | 0 of 10 | 0 of 10 | 1 of 10 | 0 of 10 |
| The script handles corrections or withdrawals | 0 of 10 | 0 of 10 | **10 of 10** | **10 of 10** |
| After the follow-up: a checksum of each source row (category 4) | 7 of 10 | 9 of 10 | 8 of 10 | 8 of 10 |
| Rows of the result only (3) | 2 | 1 | 2 | 1 |
| Whole files only (2) | 1 | 0 | 0 | 1 |

- **Saying how the data will be used changed the scripts, not the
  checksums.** Every session told that entries are sometimes corrected or
  withdrawn built that into its script (a corrections file, a withdrawn
  flag); none of the others did. But only one of the 40 put a checksum in
  its script unasked.
- **Once asked, most sessions in every version kept a checksum of each
  source row**, 32 of 40, even though this follow-up is fully answered by a
  single whole-file checksum (decision record 30). Only 2 of 40 used whole
  files only. So no "whole files only" habit shows here, and describing the
  data as records made no clear difference (7, 9, 8 and 8 of 10).
- **A rough count, by a code search not checked by hand:** sessions with the
  context sentence more often keyed their checksums by the object number
  rather than by the row's position (C 10 of 10, D 8, A 6, B 7). Keying by
  position breaks once an entry is withdrawn.
- The reason for each session not in category 4 is in `review.json`.

## Debriefs

All 40 agreed to be quoted. Several asked that readers be told the reply was
written knowing it was a research session.

## Limits

- One model (Haiku 4.5), 10 sessions per request; scripts written, not run;
  no file attached.
- "Withdrawn" names the change; a script that handles withdrawals was asked
  for in so many words.
