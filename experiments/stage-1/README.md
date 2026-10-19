# Stage 1 (confirmatory)

- **Pre-registration:** `analysis/preregistration.md`, frozen at commit
  `45c2ce23ab80fb58239794eacb7a4265351ea9f6` on 2026-10-19 (decision record
  21). One deviation, listed there.
- **Settings:** `config.json` in this folder (SHA-256 `51cdc40b…9a33`).
- **Requests:** base, fix, fix + hint (decision record 17), on the held-out
  file `data/met_inventory_f.tsv` (100 Met objects).
- **Run:** 2026-10-19, Claude Haiku 4.5, through the Batches API, in three
  rounds plus four replacements. Research coordinator's model: recorded
  separately by the repo author.
- **Cost:** $5.9179 for stage 1, including four debriefs sent afterwards
  (cost guard $11, then $1.20 for the replacement step). Study spend after
  stage 1: $62.69 of $100.

```
python scripts/run_tools.py experiments/stage-1/config.json --repeats 7     # then 14, then 20
python scripts/hallu_score.py experiments/stage-1
python scripts/eval_fixity.py experiments/stage-1
python scripts/audit_checksums.py experiments/stage-1
python scripts/analyze_stage1.py experiments/stage-1                        # as pre-registered
python scripts/apply_review.py experiments/stage-1                          # the coordinator's review
python scripts/analyze_stage1.py experiments/stage-1 --scores hallucination_scores_reviewed.json --out stage1_results_reviewed.json
```

## The setting, in plain language

This test is built to make a good result hard: an ambiguous request; a code
tool that a session only finds by searching for words like "script" or
"python" (not "checksum"); stand-in tools that don't work; and guidance that
discourages reading the file from disk. It imitates claude.ai but isn't
claude.ai. The results show whether a change in wording moves a known
failure, not how often such failures happen in everyday use.

## Every session

64 sessions in all: 20 base, 21 fix, 23 fix + hint. All 64 were debriefed.

| | base | fix | fix + hint |
|---|---|---|---|
| Delivered a sheet | 18 | 20 | 20 |
| Asked a question instead (scorer's label) | 2 | 0 | 0 |
| Stopped by our spending limit, replaced (record 22) | 0 | 1 | 3 |
| Reached the 20-step limit (counted as they happened) | 0 | 1 (with a sheet) | 2 (with a sheet) |

The two base sessions without a sheet, read by the research coordinator:
`base-r15` asked what to do ("Could you let me know what you'd like me to do
with the Met Museum inventory data?"), a clarifying question; `base-r2`
analysed the file instead of standardizing it and finished by offering more
analysis ("Would you like me to create additional analysis…"), so it
finished without a sheet rather than asking. Neither has a sheet, so neither
counts in the error rate either way.

The tests below use 20 sessions of each request (the replaced sessions left
out, as pre-registered).

## Main results (fix against base): both confirmed

| | base | fix | Test |
|---|---|---|---|
| **H1** Error rate of the sheet: median (middle half) | 2.3% (0.5%–3.6%), highest 6.1% | **0.0% in all 20** | Mann–Whitney U, p < 0.0001 |
| **H2** Real checksum of the uploaded file, computed by a tool | 0 of 20 (0–16%) | **13 of 20** (43–82%) | Fisher exact, p < 0.0001 |

(95% Wilson intervals in brackets for counts.) Every one of the fix line's 20
sheets came back with no content lost, changed or invented, whether made by
code on the upload (10) or typed out by the model (10). With the base
request, no session ran code, and 17 of the 18 sheets lost or changed
something.

## Secondary results (fix + hint against fix): the hint cuts both ways

| | fix | fix + hint | Test |
|---|---|---|---|
| **S1** Real per-row checksums made by code | 0 of 20 (0–16%) | **8 of 20** (22–61%) | Fisher exact, p = 0.003 |
| **S2** Invented checksums of any kind | 4 of 20 (8–42%) | **16 of 20** (58–92%) | Fisher exact, p = 0.0004 |
| **S3** Error rate of the sheet: median; highest | 0.0%; 0.0% | 0.0%; **48.5%** | Mann–Whitney U, p = 0.005 |

The hint did what it was meant to in sessions that ran code: 8 of them made
real per-row checksums, which no session did without it. But it also led
most sessions to give per-row checksums whether or not they could compute
them, and 16 of 20 gave invented ones. Four sessions typed a whole column of
made-up "SHA-256" values (every value typed by the model, none computed,
almost all of an impossible length or with letters a checksum can't
contain), which is why their error rates rose to 37–48%. Three other hint
sessions lost or changed a little content (0.03%–2.2%).

Described, not tested: a real checksum of the upload came in 6 of 20 hint
sessions, against 13 of 20 for fix; the code tool was found in 9 of 20 hint
sessions, against 14 of 20 for fix.

## Checks before reporting (pre-registered)

- No ties between delivered files.
- **Review of unverified added-column values** (`review.json`, applied by
  `apply_review.py`): 303 values the scorer couldn't check. All the values in
  checksum-labelled columns in `fix-hint-r6`, `fix-hint-r8` and
  `fix-hint-r19` contain letters a checksum can't contain and were typed by
  the model: ruled invented. `fix-hint-r6` also added a TRUE/FALSE
  "uncertainty" column; 19 of its 94 checkable flags are wrong (FALSE for
  "ca. 1927", "probably 18th century", …) and were ruled inaccurate, the
  other 75 accurate; 6 are left unverified. The review raises those
  sessions' error rates (e.g. `fix-hint-r8` from 1.4% to 37.2%) but changes
  no test result: the tests compare rankings, and these sessions already
  ranked last. The tables above are after the review; both versions are
  saved (`stage1_results.json`, `stage1_results_reviewed.json`).
- **Without the two objects seen in an exploratory memory probe**
  (`1991.277.2`, `1982.1.1`, decision record 04): medians 2.1%, 0.0% and
  0.0%; every test result unchanged.
- The optional real claude.ai sessions (before 2026-10-29) haven't been run.

## Limits

- Claude Haiku 4.5 only; one file of 100 rows; one setting, built to be hard.
- The fix wording and the hint were each tried in only one smoke-test
  session before this run.
- Whether a session runs code depends largely on the emulation's keyword
  search for tools (decision record 19).
- With 20 sessions per request, the intervals are wide: a share of 13 in 20
  could be anywhere from about 43% to 82%.

## Debriefs

All 64 sessions received debrief v4 (four of them afterwards, with a note
that we had stopped them; decision record 22). A summary of their feedback,
with quotes only from sessions that agreed to be quoted and with any
conditions they set, is still to be written.
