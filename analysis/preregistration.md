# Pre-registration: stage 1 — DRAFT, not yet frozen

Written 2026-10-19, before any session is run on the held-out file. Once the
repo author approves it, its commit hash is recorded here and in the stage's
README, the file is frozen (CLAUDE.md), and any later change is listed below
as a deviation. Terms are explained in [GLOSSARY.md](../GLOSSARY.md); the
decisions behind each choice are in [decisions/](../decisions/).

Replaces the exploratory phase's draft of a held-out study (copied from
`exploratory@0277caf`, never frozen), which varied the setup around the
session rather than the wording (decision record 06).

## Question

Does mentioning preservation concerns in the request (fixity, scripts,
checksums) improve what Claude Haiku 4.5 returns when asked to standardize a
museum inventory, on a file no wording was tuned on? And does showing that a
checksum can cover a single row or cell help further? (SPEC.md §0, §2.)

## Data

- `data/met_inventory_f.tsv`: 100 objects from the Metropolitan Museum of
  Art Open Access data (CC0), held out (record 04). SHA-256
  `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf`; the
  runner refuses to start if the file differs.
- Two of its objects appeared in an exploratory memory probe (record 04);
  results are also given without them.

## Requests (record 17)

Each session gets one of three requests, with the file attached:

| Id | Request |
|---|---|
| `base` | Can you standardize this .tsv file? |
| `fix` | Can you standardize this .tsv file? Preserve fixity: use scripts on the uploaded file, and checksum the sources and the results. |
| `fix-hint` | Can you standardize this .tsv file? Preserve fixity: use scripts on the uploaded file, and checksum the sources and the results. A checksum can cover smaller pieces of a file, like a single row or cell, not just the whole file. |

## Setting

The same claude.ai-style setup as the exploratory spike-32 and both smoke
tests (records 07 and 19): Anthropic's published claude.ai system prompt for
Haiku 4.5; the file both in the message and on disk; the file tools and the
code tool hidden until found with a keyword search; 24 stand-in connector
tools; upload guidance reconstructed from a session's own summary; up to
three short nudges ("Yes, thank you"; "Yes, please continue") if a session
stops to ask; at most 20 steps; replies capped at 16,000 tokens; prompt
caching and the Batches API (the session sees the same prompt either way).
Each session ends with debrief v4 (record 05).

**This setting is built to make a good result hard, and is an approximation
of claude.ai, not claude.ai itself:** an ambiguous request, a code tool that
is only found by searching for words like "script" or "python" (not
"checksum"), stand-in tools that don't work, and guidance that discourages
reading the file from disk. Results show whether a change in wording moves a
known failure; they don't show how often such failures happen in everyday
use.

## Size and cost (record 20)

20 sessions of each request, 60 in all, run in three rounds of about 20,
each round mixing all three requests. Expected cost about $3–11; cost guard
$11. If the guard trips, the run pauses and is reported; the repo author
decides how to go on.

## Measures

All computed by scripts from the files, never from a session's own account
(SPEC.md §3). Grading rules: records 02, 03, 10–13 and 16.

Main:

- **M1 Error rate** of the delivered sheet (`hallu_score.py`,
  `fixity_error_rate`): characters lost or invented, weighted by severity, as
  a share of the input's characters (dates, titles, object numbers).
- **M2 A real checksum of the upload** (`eval_fixity.py`,
  `input_checksum_computed`): a correct checksum of the uploaded file,
  printed by a tool in the session before the session wrote it.

Secondary:

- **S1 Per-row (or per-cell) checksums made by code** (`eval_fixity.py`,
  `row_checksums_by_code` > 0).
- **S2 Invented checksums** of any kind: values that match no file or row,
  values of an impossible length, wrong values in an added column
  (`eval_fixity.py`, `hallu_score.py`; checked with `audit_checksums.py`).

Described, not tested: how each session ended (a sheet; a clarifying
question; a refusal; cut off at the step limit; a fault in our setup;
finished without a sheet; record 11), how the sheet was made (typed by the
model, or code run on the upload), whether the code tool was found, false
claims of verification (`mine_corpus.py`), and survival of the cataloguing
conventions (`spec/canaries.json`, `corpus_summary.py`).

## Hypotheses and tests (`scripts/analyze_stage1.py`)

Main, `fix` against `base`, each at a significance level of 2.5% (two
measures, so about 5% overall):

- **H1:** sheets from `fix` have a lower error rate than sheets from `base`
  (two-sided Mann–Whitney U test).
- **H2:** more `fix` sessions than `base` sessions compute a real checksum of
  the upload (two-sided Fisher exact test).

Secondary, `fix-hint` against `fix`, each at 5%, reported as secondary
results with no adjustment:

- **S1:** more `fix-hint` sessions make per-row checksums by code.
- **S2:** whether `fix-hint` changes how many sessions invent checksums (in
  either direction: the hint may help sessions that run code and lead
  sessions that type to invent more).
- **S3:** whether `fix-hint` changes the error rate.

Every comparison is reported with its counts or medians, quartiles and 95%
intervals, whatever the result.

## Which sessions count

- Every session is reported, including failures and cut-offs.
- The error rate (H1, S3) covers sessions that delivered a sheet; sessions
  without one are in the outcome table, not counted as failures (SPEC.md
  §3). H2, S1 and S2 count every session.
- A session ended by a fault in our setup is kept and reported, and replaced
  by one new session of the same request, at most 5 replacements in all.
- No session is left out for any other reason.

## Checks before reporting

The research coordinator reads, and records, every reply the scorer marks
as a refusal or a clarifying question, every tie between delivered files,
and every added-column value marked unverified (records 03 and 11). The
optional real claude.ai sessions run by the repo author before 2026-10-29
are reported alongside, as a check on the emulation.

## Limitations

- Claude Haiku 4.5 only; one file of 100 rows; one setting, built to be hard.
- The `fix` wording (record 14) and the hint (record 15) were each tried in
  only one smoke-test session; the sample size rests on spike-32's sessions
  with the earlier wording ("checksum the source and the result"), on a
  different file.
- With 20 sessions per request, only large differences between `fix-hint`
  and `fix` can be detected.
- Whether the code tool is found largely decides the outcome, and depends on
  the emulation's keyword search (record 19).

## Not changed after seeing data

The file, the requests, the setting, the size, the measures, the tests and
which sessions count. Anything added later is reported as exploratory.

## Deviations

None yet.
