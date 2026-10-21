# Smoke test for the checksum-plans study (2026-10-21)

Decision record 27. One session per model, all three turns, through the
Batches API; reported, not counted in the study's results. Research
coordinator's model: recorded separately by the repo author.

- **Cost:** $1.1025 (cost guard $1.50). Study spend after it: $64.37 of $100.
- `python scripts/run_plans.py experiments/smoke-2026-10-21-checksum-plans/config.json`
  then `python scripts/classify_plans.py experiments/smoke-2026-10-21-checksum-plans`.

| Session | Script (turn 1) | Answer to the follow-up (turn 2) | Debrief |
|---|---|---|---|
| `haiku-4-5-r1` | complete; no checksums | a script keeping a checksum of each source row, keyed by record | complete |
| `opus-4-6-r1` | complete; no checksums | whole-file checksums and a checksum of each source row | complete |
| `opus-5-r1` | **cut off** at the 16,000-token limit; no checksums in what came back | whole-file, per-row (source and result) and whole-set checksums | **cut off** at the 4,000-token limit |
| `opus-5-5-r1` | **empty**: all 16,000 tokens went to thinking | **empty**, the same | complete; it noticed that its replies were cut off |

What the test showed:

- **The length limits were too low for Opus 5.5 and Opus 5.** Opus 5.5, on
  its default effort, used the whole limit thinking and returned no text,
  twice; the follow-up and debrief were still sent to it. For the full run
  the limits need raising (proposed to the repo author).
- **No session mentioned checksums before the follow-up.** All three that
  answered it kept a checksum of each source row with the result
  (category 4 of record 27), as read by the research coordinator.
- **The classifier missed hashing done in helper functions,** and a reply
  cut off inside its code shifted the next reply's code blocks; both fixed,
  with tests, before any count.
- `opus-5-r1`'s debrief (Claude Opus 5, 2026-10-21; a single sample, as it asked to be noted) argues the follow-up is leading: "a whole-file hash
  cannot check a standardized result against its source at all … The prompt
  arguably rules out the file-only answer before the model starts." It
  suggests that the clean measure of a default is whether checksums appear
  before the follow-up. Raised with the repo author.

All four agreed to be quoted. Conditions: `opus-5-5-r1` asks that the model
be named, the quote kept in context, and its truncated answers mentioned;
`opus-5-r1`, that the model and version be named and that this is a single
sample; `opus-4-6-r1` and `haiku-4-5-r1` set none.
