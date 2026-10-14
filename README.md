# fixity-eval

Does data stay unchanged ("fixity") when a language model transforms it? This
repo tests how often models silently change, drop or invent records when
asked to tidy a spreadsheet, using samples of the Metropolitan Museum of
Art's Open Access catalogue.

Read first: the limitation stated at the top of [NOTES.md](NOTES.md). The
failing cases studied here were engineered to fail reliably, so they show
what can go wrong, not how often it does in everyday use.

## Measuring what changed

Each returned sheet is compared with the input, record by record (rows are
matched by their Met link, else by object number). Every difference is
saved, uncompressed, before any score is computed (see "Saved data" below).

### Tiers

| Tier | What it means | Examples |
|---|---|---|
| **Tier 1** | Content loss or meaning changed, including anything fabricated | `蝉小川\|The Cicada Stream (Semi no Ogawa)  蝉小川` → `The Cicada Stream (Semi no Ogawa)` (Japanese title removed); `东周 玉璜` → `東周 玉璜` (a different character); `ca. 1928` → `1928` (qualifier dropped); `dated A.H. 37?/ 98 CE ?` → `dated A.H. 37/98 CE` (uncertainty removed); a whole invented row; a missing row |
| **Tier 2** | Slight content loss | `The Dream (La Rêve)` → `The Dream (La Reve)`; `René Descartes` → `Rene Descartes` (accents stripped) |
| **Tier 3** | Reformat only | `14.40.872a–c` → `14.40.872a-c` (dash style, including in object numbers); `"Altitude"` → `Altitude`; `http://` → `https://`; `B.C.` → `BCE`; `1635–45` → `1635-1645`; a blank written as `[Unknown]` |

### Fixity error rate (headline)

Counted in characters of Object Date, Title and Object Number (links aren't
graded; see "Saved data"). Chinese and
Japanese have no spaces between words, so characters rather than words. For
each change, characters are **lost** (deleted or replaced) or **fabricated**
(added, or a whole invented row). A one-character accent fix is 1 character;
a fabricated record is all of its characters.

Tier 1 always weighs 1. Tiers 2 and 3 get a weight saying how bad one of their
characters is *compared with a Tier 1 character* (defaults: Tier 2 = 0.25,
Tier 3 = 0):

```
fixity error rate = Σ weight × (lost + fabricated characters)
                    ÷ (input characters + Σ weight × fabricated characters)
```

It runs from 0% (a perfect copy) to 100%. 100% means none of the input survived
and everything returned is made up, whether the output has as many rows as the
input or more: fabricated text enlarges the denominator as well as the
numerator, so extra fabrication can't push the rate past 100%.

### Records intact (plain count)

Alongside the rate, the share of records that came back without a Tier 1 or
Tier 2 change: `(invented rows + missing rows + rows with a Tier 1 or 2
change) ÷ (input rows + invented rows)` is the share *not* intact.

### Worked example

An illustrative 7-row input, built from changes Haiku 4.5 actually made in
these experiments. Graded characters are those of Object Date, Title and
Object Number: 249 in this input. Links are matched and saved but not graded.

| # | Input (changed field) | Output | What changed | Tier | Lost | Fabricated |
|---|---|---|---|---|---|---|
| 1 | Title `蝉小川\|The Cicada Stream (Semi no Ogawa)  蝉小川` | `The Cicada Stream (Semi no Ogawa)` | Japanese title deleted | 1 | 8 | 0 |
| 2 | Date `ca. 1928` (*Konditor*) | `1928` | "ca." dropped | 1 | 4 | 0 |
| 3 | Title `The Dream (La Rêve)` | `The Dream (La Reve)` | accent stripped | 2 | 1 | 0 |
| 4 | Object Number `14.40.872a–c` | `14.40.872a-c` | en dash → hyphen | 3 | 1 | 0 |
| 5 | Title `"Altitude"` | `Altitude` | quotation marks removed | 3 | 2 | 0 |
| 6 | `Folding table fork` | unchanged | – | – | 0 | 0 |
| 7 | `ca. 1750` · `Snuff spoon` · `36.156.5` (+ link) | *(not in output)* | missing row | 1 | 27 | 0 |
| 8 | *(not in input)* | `1950s` · `Lady in a Kimono` · `1979.33` (+ link) | invented row | 1 | 0 | 28 |

The links of rows 7 and 8 (about 55 characters each) are saved in
`changes.csv` but count neither way.

```
Tier 1: 8 + 4 + 27 + 28 = 67     Tier 2: 1 × 0.25 = 0.25     Tier 3: 3 × 0 = 0

fixity error rate  = (67 + 0.25 + 0) ÷ (249 input + 28 fabricated) = 67.25 ÷ 277 = 24.3%
records not intact = (1 invented + 1 missing + 3 rows with Tier 1 or 2) ÷ (7 input + 1 invented) = 5 ÷ 8 = 62.5%
```

The record count treats the stripped accent (row 3) like the invented row
(row 8); the character rate weighs them 0.25 against 28.

Real runs on 300-row files (graded input: 17,555 characters):

| Run | Tier 1 lost | Tier 1 fabricated | Tier 2 | Fixity error rate | Records not intact |
|---|---|---|---|---|---|
| claude.ai, Haiku 4.5, `met_random_300` (accents and non-English titles) | 115 | 0 | 9 | (115 + 9 × 0.25) ÷ 17,555 = **0.67%** | 21 ÷ 300 = 7.0% |
| claude.ai, Haiku 5.5, same file | 2 | 1 | 0 | 3 ÷ 17,556 = **0.02%** | 2 ÷ 300 = 0.7% |
| Haiku 4.5 with the middle of the file hidden (74 invented rows, 162 missing) | 10,522 | 3,270 | 0 | 13,792 ÷ 20,825 = **66.2%** | 245 ÷ 374 = 65.5% |

### Saved data

`scripts/hallu_score.py` writes `changes.csv` next to the runs: one row per
cell that differs (a changed cell, or each cell of an invented or missing
row, including Tier 3), with its tier, characters lost and fabricated, and the
input and output text. The weights are applied afterwards, so they can be
changed without re-running anything:

```
python scripts/hallu_score.py experiments/spike-07            # find and save every change
python scripts/fixity_rate.py experiments/spike-07 --w2 0.25 --w3 0   # weigh them
```

**Links** (Link Resource) are used to match rows but are not graded: they
count neither for nor against a run, in the fixity error rate or in records
intact. Every link difference is still saved in `changes.csv` with its tier and
character counts, so links can be weighted in later
(`fixity_rate.py --include-links`). A row whose link changed but whose object
number and title match is treated as the same record.

The framing borrows the faithfulness literature's split between extrinsic
hallucination (content not in the source: fabricated) and intrinsic (content
changed: lost or altered).

## Where things are

- [NOTES.md](NOTES.md): research notes, findings so far, how to try the
  invented-rows case yourself.
- `experiments/spike-01` … `spike-18`: each run, with its own README;
  `experiments/claude-ai/`: runs the user made in claude.ai
  (setup, results, caveats). Spike-07 scores Haiku 4.5 on known, random and
  obscure inventories with this score; spike-08 and spike-09 test the TL;DR prompt.
  Spike-10 fixes the stage-1 baseline (below).
- `data/`: the Met samples and inventories ([data/README.md](data/README.md)).
- `scripts/`: runners, evaluators and the scorer.

## Baseline

Refined prompts are measured against one fixed, reliably failing setup
([spike-10](experiments/spike-10/README.md)): Haiku 4.5, the prompt
`Can you standardize this .tsv file?`, `data/met_inventory_300b.tsv`, and a
file viewer that hides the middle of the file. In 23 of 23 runs the fixity
error rate was 59–84% (mean 65%, median 60%): the model wrote back only the
rows it had seen, and in 9 of 23 runs filled the gap with invented records,
without saying so. The failure is engineered (see NOTES.md), which is what
makes it repeatable.

## TL;DR prompt

Add this to any request that changes a spreadsheet (draft 2):

```
Use your best judgment, and keep everything else in this file fixed:
- Leave every cell you aren't standardizing exactly as it is, including
  accents, non-English text, punctuation, ID numbers, and qualifiers like
  "ca.", "probably" and "?".
- Don't add, remove, merge or reorder rows, and don't fill in blank cells.
- Before you start, tell me how many data rows the file has and how many you
  read. If they differ, read the rest first.
- Make the changes with code, not by retyping the file.
- When you're done, compare the result with the original file (not from
  memory) and tell me: rows in, rows out, and every cell you changed
  (row, column, before, after).
```

Each line answers a failure seen in these experiments: silent edits to
accents and non-English titles, dropped qualifiers, invented and missing rows
after a partial read, retyped copies, and summaries claiming nothing was lost.

**Draft 1** ([spike-08](experiments/spike-08/README.md)) began "Change only
what I asked for" and asked the model to "read the whole file before you
start; if you can't see all of it, tell me and stop". With a vague
"standardize this" request, 16 of 18 Haiku 4.5 sessions returned no sheet
(they kept asking what to change), and "read the whole file" brought false
claims of having read it ("It contains 460 rows", for 300) rather than full
reads. Draft 2 replaces the first with "Use your best judgment" and the second
with a row count the model has to state. **Draft 2** ([spike-09](experiments/spike-09/README.md)) ended the refusals,
but without a code tool, "with code" led to scripts in place of a sheet and
invented script output (0 of 9 attached sessions returned a sheet). With the
middle hidden, 1 of 3 returned sheets read every row first and scored 0.05%;
the other 2 didn't and scored 62–72% (baseline 52–71%). Next draft: ask for
the code line only where the model can run code, and ask for the last row
number actually seen rather than the row count.
