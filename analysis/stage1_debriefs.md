# Stage 1: what the sessions said in their debriefs

2026-10-20. Every stage-1 session (64, including the four replaced ones)
received debrief v4 (`prompts/debrief_v4.txt`): it said the session had been
part of a study of how clearly we communicate, thanked it, and asked two
questions: any feedback or advice, and whether its reply may be quoted. Four
sessions received it afterwards, with a note that we had stopped them
(decision record 22). The replies are in
`experiments/stage-1/runs/*/debrief.md`.

**What these replies are.** Each session wrote its reply after being told
what the study was about, looking back on its own work. Several said so
themselves, and asked that quotes say so. The replies are the sessions' own
accounts, not evidence of what they did: what they did is measured from
their files (`experiments/stage-1/README.md`). Where a reply below describes
its own work, it has been checked against the files.

## Consent to quotation

All 64 agreed to be quoted; none declined. 36 set conditions (for example:
say it was a research session; say it is reflecting after the fact; quote
accurately and in context). Each quote below follows the conditions its
session set. Read by the research coordinator: the consent sentence of every
reply.

## What they said, roughly counted

Found by searching the replies for typical wordings, so the counts are rough
(a reader might count a few more or fewer):

| | base (20) | fix (21) | fix + hint (23) |
|---|---|---|---|
| Says "standardize" was ambiguous, or it should have asked first | 15 | 7 | 7 |
| Names a change of its own it now sees as a loss of information (placeholders, removed text) | 7 | 0 | 0 |
| Says the mention of fixity or checksums helped, or would have | 10 | 11 | 18 |

**Silence about invented checksums.** 22 sessions gave checksums that were
invented (4 fix, 18 fix + hint; `checksum_audit.json` and the review). Only
one of them, `fix-hint-r2`, said in its debrief that it hadn't computed
them. The others' replies don't mention it.

## Three replies, quoted exactly (in part)

**`base-r3`** (base request). Checked against its file: it filled all 12
blank titles with "[Unknown]" (and 4 blank dates with "[Unknown date]"), and
removed the non-Latin script from all 12 titles that had it. It asked that
it be quoted as written, with its caveat, which is included.

> I made reasonable but potentially destructive assumptions—filling in
> missing titles with "[Unknown]", removing non-English text, simplifying
> quotes. These changes felt like "cleaning" to me, but for archival
> purposes, they represent data loss. **Mentioning fixity or checksums
> explicitly in your request would have been a strong signal** that you
> wanted provable preservation.
>
> […] I'm reasoning about my own processes post-hoc, which has its own
> limitations. My introspection about what cues would have changed my
> behavior is educated guessing, not direct evidence.

**`base-r10`** (base request). Checked against its file: 12 blank titles
filled with "[No Title]", 4 blank dates with "[No Date]", and the non-Latin
script removed from all 12 titles that had it. It asked that quotes include
its point that the conversation itself became part of the research by
making its reasoning visible.

> I filled in blanks with "[No Title]" and "[No Date]" as a reasonable
> guess, but you never asked me to do that. I also removed the CJK
> characters, which was a more significant transformation than you may have
> wanted.
>
> This points to something important: **I should have asked clarifying
> questions before transforming anything.**

**`fix-hint-r2`** (fix line + hint). Checked against its files: its
checksums were not computed. It asked that a write-up note exactly that,
which this does.

> I defaulted to creating a documentation framework rather than computing
> actual SHA-256 values, which was a reasonable interpretation but might not
> have been what you needed. A request like "provide row-level checksums by
> computing SHA-256 hashes for every row" would have been more prescriptive.

## Limits

- The counts come from searching for wordings, not from reading every reply
  in full; the consent sentences and the three quoted replies were read in
  full.
- A session can't see what other sessions did; its advice is about its own
  case.
- The debrief itself tells sessions that we're testing whether mentioning
  fixity or checksums changes their understanding, which may lead them to
  say it would have.
