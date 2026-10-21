# 30. A 2×2 study: does describing the data, or how it will be used, change checksum plans?

- **Date:** 2026-10-21
- **Status:** approved by the repo author in chat, 2026-10-21 (wordings,
  design, size and cost guard).

## Context

In the checksum-plans study (records 26, 27 and 29) no session put a
checksum in its script unasked, and every session planned a checksum of each
source row once the follow-up named the need, a follow-up that leads that
way. The repo author's point: we describe data to models as "a file", which
may steer them to whole-file checksums; and saying how the data will be used
later (records corrected or withdrawn one at a time) is what makes per-record
checksums worth having.

## Decision

- **Four requests**, two changes crossed (`prompts/wrap_A.txt` … `wrap_D.txt`):

  | | Described as a file | Described as records |
  |---|---|---|
  | No context of use | A | B |
  | "Individual entries are sometimes corrected or withdrawn later." | D | C |

  A is the checksum-plans request. The added sentence says "entries", not
  "records" or "rows", so that only the context differs.
- **Follow-up**, the same for all (`prompts/wrap_followup.txt`, the repo
  author's wording): "If you were to use checksums, to verify that the source
  data hasn't changed, how would you incorporate that?" A whole-file checksum
  answers it fully, so it doesn't steer towards finer ones.
- **Debrief** v6 (`prompts/debrief_v6_wrappers.txt`): v5 with its second
  sentence changed to describe this study.
- **Model:** Claude Haiku 4.5 on its API defaults, 10 sessions per request,
  40 in all, through the Batches API; cost guard $3 (expected about $1.40).
  First a smoke test of one session per request (guard $0.50); if all four
  come back complete, the full run follows.
- **Measured** as in record 27 (categories set there), plus: whether
  checksums come up before the follow-up, and, for C and D, whether the plan
  says what happens to checksums when an entry is corrected or withdrawn.
  The main comparison is the share of per-record answers across A–D.
- **Exploratory and descriptive.**

## Consequences

- Ten sessions per request can show a large difference, not a small one.
- One model; scripts written, not run; no file attached.
