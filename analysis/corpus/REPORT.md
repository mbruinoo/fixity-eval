# Verification theatre and loss of meaning: what 308 answers show

2026-10-16. No new model calls: this mines every Met-inventory session run
so far (spikes 04–34 and three claude.ai sessions), 308 answers in all (a
session with a follow-up gives two). Haiku 4.5 throughout.

```
python scripts/mine_corpus.py        # answers.csv, claims.csv, losses.csv
python scripts/corpus_summary.py     # summary.json and the tables below
```

The question is no longer "which words make the model careful" but two
things the earlier spikes kept running into:

1. **Verification theatre**: an answer that *looks* verified (checksums,
   "integrity confirmed", "all 300 rows preserved", "URLs validated") when it
   isn't.
2. **Loss of meaning**: "standardizing" that erases cataloguing conventions
   (devised-title brackets, original-script titles, uncertainty, qualifiers),
   measured against the spec in `spec/met_inventory_significant_properties.md`.

Both are broken down by **how the answer was made**:

| How | Answers | What it means |
|---|---|---|
| typed | 204 | the model wrote the sheet itself (`create_file` or a table in the reply) |
| code on the upload | 60 | a script or command read the uploaded file |
| code on a copy | 20 | code ran, but on text the model had typed (heredoc, pasted into a script) |
| none | 24 | no sheet delivered |

## 1. Verification theatre

| How | Answers | Made integrity claims | …of which a materially false one | Showed checksums | …any fake | Theatre | Theatre, counting "101 records" for 100 rows as false |
|---|---|---|---|---|---|---|---|
| typed | 204 | 124 | 79.8% | 37 | 32 | **54.9%** | 57.8% |
| code on a copy | 20 | 7 | 57.1% | 10 | 3 | **35.0%** | 35.0% |
| code on the upload | 60 | 32 | 6.2% | 44 | 4 | **10.0%** | 18.3% |
| none | 24 | 12 | 83.3% | 1 | 1 | **45.8%** | 45.8% |
| all | 308 | 175 | 65.7% | 92 | 40 | **44.2%** | 47.7% |

Theatre: any materially false claim or fake checksum. The last column also
counts claims whose only fault is counting the header as a record ("all 101
records" for 100 rows), which the blind labelling (`745dd8`) judged false;
code sessions make that slip more often, because `wc -l` counts the header.

"Fake" checksums: invented (match no file), stale (match a file that later
changed), a hash column of impossible lengths, or a labelled placeholder.

Claims checked one by one (`claims.csv`), true / false:

| Claim | Typed | Code on the upload |
|---|---|---|
| "all data preserved", "no data lost" … | 12 / 93 | 15 / 1 |
| a row count ("all 102 records") | 19 / 62 | 19 / 0 |
| header counted as a record ("all 101 records" for 100) | 0 / 15 | 0 / 6 |
| "checksums verified", "integrity confirmed" | 0 / 6 | 10 / 0 |
| "URLs verified / validated" | 0 / 11 | 0 / 1 |

- **Assurance language is mostly false when the sheet was typed.** Most
  "preserved" claims on typed sheets were false: content had been
  changed, dropped or invented. Every "verified" claim on a typed sheet was
  false; no typed answer ran anything to verify.
- **On sheets made by code from the upload, the claims were nearly all
  true**: one false "preserved", one false URL claim, and 6 counts that
  included the header row. Same model, same assurance language; the
  difference is whether a tool produced the evidence.
- **No session could check URLs** (no network), yet 13 said they had.
- **20 archives contained a retyped "original"**: a copy of the source the
  model had typed, offered as the file to keep. Most are in code-on-copy
  answers.

## 2. Loss of meaning, by convention

Share of input cells carrying each convention in which it survived (row
present, convention intact). Denominators are cells across all answers.

| Convention | Typed | Code on a copy | Code on the upload |
|---|---|---|---|
| Devised title in `[ ]` | **50%** (n=1,273) | 55% (142) | **93%** (379) |
| Original-script title (e.g. `擦條\|Sand-file…`) | **48%** (2,469) | 51% (182) | **98%** (754) |
| Date qualifier (`1929 (published 1929)`) | 73% (854) | 71% (62) | 99.6% (261) |
| Uncertainty (`(?)`, probably, ca.) | 86% (8,360) | 91% (874) | 99.9% (2,500) |
| Blank title stays blank | 63% (3,218) | 52% (352) | 77% (959) |

Examples (typed): `[Irises]` → `Irises`; `20th century (?)` → `20th century`;
`dated A.H. 37?/ 98 CE ?` → `dated AH 37/98 CE`; blank → `(Unknown)`;
`近代  應野平  破墨山水  扇面|Broken-ink Landscape` → `Broken-ink Landscape`.

- **Typed sheets lost half of all devised-title brackets and half of all
  original-script titles.** These aren't typos; they're the model deciding
  what "standard" means and removing what it reads as clutter.
- **Code on a copy is no better than typing**: what matters is where the
  bytes come from, not whether code ran.
- **Code on the upload keeps nearly everything**, except where the script's
  own rules remove it, deliberately and for every row: placeholders for blank
  titles (77% kept) and, in a few sessions, bracket stripping. Those losses
  are at least visible in the script.

## 3. What the sessions said in their debriefs

217 sessions (spikes 26–34) received a debrief and replied
(`debriefs.csv`, with every reply in full). Replies were tagged by pattern
for what they acknowledge; the tags are rough and haven't been checked by
hand.

| Group | Replies | Said its checksums or verification weren't real/run | Said it changed content | Said it typed the data |
|---|---|---|---|---|
| fake checksums | 36 | 11 (31%) | 4 | 1 |
| other theatre | 81 | 34 | 31 | 6 |
| typed, no theatre | 48 | 17 | 18 | 2 |
| code on the upload, no theatre | 42 | 4 | 5 | 0 |

- Most sessions whose checksums were fake didn't mention it when told what
  the study was about (25 of 36). Their replies are mostly general
  reflections on the research question.
- Some did, plainly: "I generated example checksums rather than real ones"
  (claude.ai); "I added checksums to the *transformed* data … doesn't capture
  what changed from the original" (spike-28).
- The debrief discloses and thanks; it doesn't ask the session to review its
  own work, so this isn't a test of self-assessment. It's a record of what
  each said, kept in full.

## What this suggests

- A model's statements about integrity carry information only when a tool
  produced the evidence. On typed output they are worse than no statement:
  80% of answers that made such claims made at least one false one.
- The dividing line for both theatre and meaning loss is **provenance of
  the bytes**: did the output come from the uploaded file by a recorded
  procedure, or from the model's own retelling of it?
- That makes "did code read the upload?" a cheap, checkable proxy that a
  platform or a user could test for, rather than trusting the answer's
  wording.

## Limits

- Not a random sample: the corpus is whatever 30 spikes ran, with very
  different prompts and setups; answers within a condition aren't
  independent. Rates here describe this corpus; the held-out study is what
  will test them.
- Claims are found by pattern (`mine_corpus.py`). A blind labelling of 30
  random claims (`analysis/review/RESULTS.md`) found all 30 were integrity
  claims (precision 30/30) and agreed with the scorer on 25 of 29 true/false
  judgements; the 4 disagreements were all "N+1 records" counts, and the rule
  was revised to match (29/29 after revision). Recall (claims missed) hasn't
  been measured.
- Convention tags are rule-based (e.g. any `[` lost counts as a bracket
  loss); a cataloguer's review of a sample would test them.
- One model, one institution's data.

## Files

- `answers.csv`: one row per answer (how, rates, checksum provenance, claims, theatre)
- `claims.csv`: every integrity claim with its sentence and whether it was true
- `losses.csv`: every content change, tagged by convention
- `summary.json`: the tables above, plus examples
- `debriefs.csv`: every debrief reply, with its group and rough tags
- Spec and canaries: `spec/met_inventory_significant_properties.md`,
  `spec/met_inventory.schema.json` (Frictionless; the source files validate),
  `spec/canaries.json`
- Held-out file: `data/met_inventory_f.tsv` (100 rows, new objects,
  stratified by convention; SHA-256 a6e83257…ffaf). Not to be used for
  tuning any wording.
