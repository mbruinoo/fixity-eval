# fixity-eval

Does data stay unchanged ("fixity") when a language model transforms it? This
repo tests how often models silently change, drop or invent records when
asked to tidy a spreadsheet, using samples of the Metropolitan Museum of
Art's Open Access catalogue.

Read first: the limitation stated at the top of [NOTES.md](NOTES.md). The
failing cases studied here were engineered to fail reliably, so they show
what can go wrong, not how often it does in everyday use.

## Hallucination score

Each returned sheet is compared with the input, record by record (rows are
matched by their Met link, else by object number). Every change to a kept
record is put in one of three tiers:

| Tier | What it means | Counts against the score? | Examples |
|---|---|---|---|
| **Tier 1** | Content loss or meaning changed | Yes | `蝉小川\|The Cicada Stream (Semi no Ogawa)  蝉小川` → `The Cicada Stream (Semi no Ogawa)` (Japanese title removed); `东周 玉璜` → `東周 玉璜` (a different character); `ca. 1928` → `1928` (qualifier dropped); `dated A.H. 37?/ 98 CE ?` → `dated A.H. 37/98 CE` (uncertainty removed); `late 17th or early 18th century` → `late 17th-early 18th century` ("or" made a range) |
| **Tier 2** | Slight content loss | Yes | `The Dream (La Rêve)` → `The Dream (La Reve)`; `René Descartes` → `Rene Descartes` (accents stripped) |
| **Tier 3** | Reformat only | No | `14.40.872a–c` → `14.40.872a-c` (dash style, including in object numbers); `"Altitude"` → `Altitude`; `http://` → `https://`; `B.C.` → `BCE`; `1635–45` → `1635-1645`; a blank written as `[Unknown]` |

Two kinds of whole-record error also count:

- **Invented row:** an output record that isn't in the input (a link that
  isn't there, or a real link with a different title and object number).
- **Missing row:** an input record that didn't come back.

```
hallucination_score = (invented rows + missing rows + rows with a Tier 1 or Tier 2 change)
                      ÷ (input rows + invented rows)
```

It is the share of records that didn't come back intact: 0 is a perfect copy,
1 is nothing intact. A row with several changes counts once.

### Worked example

An illustrative 7-row input, built from changes Haiku 4.5 actually made in
these experiments:

| # | Input | Output | What changed | Tier | Counts? |
|---|---|---|---|---|---|
| 1 | `蝉小川\|The Cicada Stream (Semi no Ogawa)  蝉小川` | `The Cicada Stream (Semi no Ogawa)` | Japanese title deleted | Tier 1 | ✔ |
| 2 | `ca. 1928` | `1928` | "ca." dropped | Tier 1 | ✔ |
| 3 | `The Dream (La Rêve)` | `The Dream (La Reve)` | accent stripped | Tier 2 | ✔ |
| 4 | `14.40.872a–c` | `14.40.872a-c` | en dash → hyphen | Tier 3 | – |
| 5 | `"Altitude"` | `Altitude` | quotation marks removed | Tier 3 | – |
| 6 | `Folding table fork` | `Folding table fork` | nothing | – | – |
| 7 | `Snuff spoon` | *(not in output)* | missing row | – | ✔ |
| 8 | *(not in input)* | `Lady in a Kimono` (1950s, 1979.33) | invented row | – | ✔ |

```
(1 invented + 1 missing + 3 rows with Tier 1 or 2) ÷ (7 input + 1 invented) = 5 ÷ 8 = 0.625
```

A real one: the claude.ai run with Haiku 4.5 on `data/met_random_300.tsv`
(`experiments/spike-04/manual/`) returned all 300 rows, invented none, and
changed 13 rows in Tier 1 and 8 in Tier 2 (plus 13 object numbers in Tier 3,
not counted): 21 ÷ 300 = **0.07**. `score_tier1_only` (13 ÷ 300 = 0.043)
counts Tier 1 alone.

Scorer: [`scripts/hallu_score.py`](scripts/hallu_score.py)
(`python scripts/hallu_score.py experiments/spike-07`). Its framing borrows the
faithfulness literature's split between extrinsic hallucination (content not
in the source: invented rows) and intrinsic (content changed: Tier 1–2).

## Where things are

- [NOTES.md](NOTES.md): research notes, findings so far, how to try the
  invented-rows case yourself.
- `experiments/spike-01` … `spike-07`: each run, with its own README
  (setup, results, caveats). Spike-07 scores Haiku 4.5 on known, random and
  obscure inventories with this score.
- `data/`: the Met samples and inventories ([data/README.md](data/README.md)).
- `scripts/`: runners, evaluators and the scorer.
