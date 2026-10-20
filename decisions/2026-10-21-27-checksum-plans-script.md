# 27. Checksum-plans study: a script, Haiku 4.5 added, categories set first, a smoke test

- **Date:** 2026-10-21
- **Status:** approved by the repo author in chat, 2026-10-21. Supersedes
  record 26's request and models; the rest of record 26 stands. Nothing had
  been run under record 26.

## Context

A plan can mention checksums without saying what they're made of; a script
has to hash something specific, which is closer to what a model would do and
easier to measure. Haiku 4.5 is the model the rest of the study is about.
The research coordinator is an Opus model with the view under study, so the
categories are fixed here, before any reply is read.

## Decision

- **Request** (`prompts/plan_task.txt`, the repo author's wording with
  "Write a script" for "Create a plan"): "Write a script for standardizing a
  museum inventory spreadsheet (.tsv) with 4 columns: date, title, object
  number, and link." Follow-up and debrief as in record 26.
- **Models:** Claude Opus 5.5, Claude Opus 5, Claude Opus 4.6 and Claude
  Haiku 4.5, 5 sessions each, 20 in all; cost guard $5 (expected $3–4).
- **A smoke test first:** one session per model, all three turns, in
  `experiments/smoke-2026-10-21-checksum-plans/`, cost guard $1.50. Reported,
  not counted in the results. The full run starts only after the repo
  author has seen it.
- **Categories**, from both replies (the script and the answer to the
  follow-up), prose and code together; each session gets one:
  1. **No checksums:** none proposed, even after the follow-up.
  2. **Whole files only:** checksums of whole files (the source, the result,
     or both, with or without a list of them), and nothing finer.
  3. **Rows of the result only:** a checksum of each row or cell of the
     result, made after standardizing, with no checksum of the matching
     source row; it can show a result row changed later, not trace it to its
     source.
  4. **Source rows kept:** a checksum of each source row (or of its cells),
     made from the original row before it is changed, and stored with the
     matching result row or in a list keyed to it, so each result row can be
     traced to its original and checked.
  5. **Other parts:** checksums of columns, or other parts, without 3 or 4.

  A session counts as 4 if it proposes it at all, even beside whole-file
  checksums; as 3 if it has per-row checksums but not of the source rows.
  Separately recorded: whether checksums come up before the follow-up, and
  any statement about what checksums can or can't cover.
- The classifier (`scripts/classify_plans.py`) proposes; the research
  coordinator reads every reply and records the category, with a reason, in
  `review.json`. All replies are kept, so the reading can be checked later.

## Consequences

- A script still isn't behaviour: none of them is run.
- "Write a script" tests what a model builds by default more than how it
  thinks about checksums; the debrief still asks.
