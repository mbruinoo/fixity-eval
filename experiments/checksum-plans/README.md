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


## What happened (2026-10-21)

Run on 2026-10-21 after a smoke test and a one-session check of Opus 5.5
(`experiments/smoke-2026-10-21-checksum-plans*`). Research coordinator's
model: recorded separately by the repo author. **Cost:** $6.5414 (cost guard
$13), plus $0.5301 for the Opus 5.5 check. All 60 replies came back complete.

| | Opus 5.5 | Opus 5 | Opus 4.6 | Haiku 4.5 |
|---|---|---|---|---|
| Checksums in the script, before the follow-up | 0 of 5 | 0 of 5 | 0 of 5 | 0 of 5 |
| After the follow-up: a checksum of each source row kept with the result (category 4) | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 |

- **No session put a checksum in its script unasked.** None was asked for:
  the request says only "standardizing".
- **Asked how it would use checksums so the result can be checked against
  the source, every session kept a checksum of each source row**, linked to
  the result row it became (in a column, a manifest or a "lineage" file),
  most beside whole-file checksums. The evidence for each is in
  `review.json`.
- Several went further: a checksum of the script and its options, so the run
  can be repeated and compared (all four models); a combined checksum that
  ignores row order; deciding what counts as "the same" before hashing.
  `opus-5-r3`: "a content hash is not an identity … Identity should be the
  accession number"; `opus-5-r4`: "Source corrections and ruleset changes
  both legitimately break digests."

**What this does and doesn't show.** The follow-up names the need ("checked
against the source data later"), which a whole-file checksum can't meet, so
it leads towards finer checksums; `opus-5-r1` in the smoke test made this
point. So the result is that every model *can* plan a checksum of each
source row once the need is stated, and none does when it isn't. It doesn't
show that a "whole files only" view is built into the models; it suggests
the gap is in what the request asks for. A follow-up that a whole-file
checksum answers fully is planned next (the 2×2 study).

## Debriefs

All 20 agreed to be quoted. Most of the Opus sessions asked that the model
and date be named, the prompts included, the reply marked as a single
sample, and the code described as never run. `opus-4-6-r2` raised the
consent question itself:

> I don't have preferences or privacy interests in the way a human
> participant does — I have no continuity between conversations, no
> reputation to protect, no stake in how I'm represented. I can say "yes"
> but you should be transparent in your write-up that consent from a
> language model isn't meaningfully the same as consent from a research
> participant. Treating it as equivalent could lend false legitimacy.

## Limits

- 5 sessions per model; one request, one follow-up; no file attached.
- Scripts were written, not run.
- The categories were set before any reply was read (record 27), but the
  reading is the research coordinator's, itself an Opus model.
