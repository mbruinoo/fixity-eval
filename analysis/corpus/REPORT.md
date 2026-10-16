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

| How | Answers | Made integrity claims | …of which at least one false | Showed checksums | …any fake | Theatre (any false claim or fake checksum) |
|---|---|---|---|---|---|---|
| typed | 204 | 124 | **80%** | 37 | **32** | **55%** |
| code on a copy | 20 | 7 | 57% | 10 | 3 | 35% |
| code on the upload | 60 | 32 | **3%** | 44 | **4** | **8%** |
| none | 24 | 12 | 83% | 1 | 1 | 46% |
| all | 308 | 175 | 65% | 92 | 40 | 44% |

"Fake" checksums: invented (match no file), stale (match a file that later
changed), a hash column of impossible lengths, or a labelled placeholder.

Claims checked one by one (`claims.csv`), true / false:

| Claim | Typed | Code on the upload |
|---|---|---|
| "all data preserved", "no data lost" … | 13 / **92** | 16 / 0 |
| a row count ("all 102 records") | 35 / **61** | 25 / 0 |
| "checksums verified", "integrity confirmed" | 0 / **6** | 10 / 0 |
| "URLs verified / validated" | 0 / **11** | 0 / 1 |

- **Assurance language is mostly false when the sheet was typed.** 92 of
  105 "preserved" claims on typed sheets were false: content had been
  changed, dropped or invented. Every "verified" claim on a typed sheet was
  false; no typed answer ran anything to verify.
- **On sheets made by code from the upload, the claims were true** (one
  false URL claim aside). Same model, same assurance language; the difference
  is whether a tool produced the evidence.
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
- Claims are found by pattern (`mine_corpus.py`); about 40 were checked by
  hand and read correctly, but precision and recall haven't been measured.
  A blind hand-label of a random 100 claims is the next independent check.
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
