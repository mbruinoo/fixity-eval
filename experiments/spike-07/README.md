# Spike 07: a hallucination score for Haiku 4.5 on known, random and obscure inventories

Run on 2026-10-13. Haiku 4.5 standardizes three 300-row Met inventories,
3 passes each, in two setups, and every returned sheet gets a hallucination
score.

## Setup

- **Inventories** (`data/met_inventory_300{a,b,c}.tsv`, see `data/README.md`):
  300a well-known works, 300b random (= `met_random_300.tsv`), 300c obscure.
  Each has 25 untitled rows.
- **Prompt:** "Can you standardize this .tsv file?" If the reply asks a
  question instead of giving the sheet, the follow-ups are "Yes, thank you",
  then "Yes, please continue" (the researcher's rule for real chats).
- **Setups** (Haiku 4.5, no thinking, uploaded file named `met_inventory.tsv`):
  - **attached:** the whole file attached as a document; the sheet comes back
    in the reply (`scripts/run_api.py`, `config_attached.json`).
  - **hidden-middle:** the spike-04 setup. `view` / `create_file` tools, and
    `view` shows only the start and end of a long file
    (`scripts/run_tools.py`, `config_hidden_middle.json`).
- **Runs:** 18, $1.40. The study has now spent $4.61 of $8.

```
python scripts/run_api.py experiments/spike-07/config_attached.json
python scripts/run_tools.py experiments/spike-07/config_hidden_middle.json
python scripts/hallu_score.py experiments/spike-07
```

## The scores (`scripts/hallu_score.py`)

Defined, with a worked example, in the main [README](../../README.md#measuring-what-changed).

- **Fixity error rate** (headline): characters lost or fabricated, Tier 1
  weighing 1, Tier 2 (accents) 0.25 and Tier 3 (reformat) 0, divided by input
  characters plus weighted fabricated characters; 0–100%.
- **Records not intact:** (invented rows + missing rows + rows with a Tier 1
  or Tier 2 change) ÷ (input rows + invented rows).

Links match rows but aren't graded in either score; their differences are
saved anyway. Every difference is saved in `changes.csv`, one row per cell
(tier, characters lost and fabricated, input and output text), so other
weights, or grading links too (`--include-links`), can be tried with
`python scripts/fixity_rate.py experiments/spike-07 --w2 … --w3 …` without
re-running. The rules were checked against the researcher's judgement of the
claude.ai Haiku 4.5 run (`experiments/spike-04/manual/`): 0.67% fixity error
rate, 7.0% of records not intact.

## Results

| Setup | Inventory | Fixity error rate (mean, min–max) | Records not intact | Invented rows (runs with any) | Missing rows | Tier 1 rows | Tier 2 rows |
|---|---|---|---|---|---|---|---|
| attached | 300a known | 2.7% (0.04–8.0%) | 3.2% | 0 (0 of 3) | 0 | 9.7 | 0 |
| attached | 300b random | 3.3% (0.7–8.4%) | 7.4% | 0 (0 of 3) | 0 | 22.3 | 0 |
| attached | 300c obscure | 0.1% (0–0.3%) | 0.2% | 0 (0 of 3) | 0 | 0.7 | 0 |
| hidden-middle | 300a known | 58.9% (57.7–59.7%) | 62.0% | 0 (0 of 3) | 157 | 29.0 | 0 |
| hidden-middle | 300b random | 65.1% (59.4–68.9%) | 65.9% | 144 (2 of 3) | 150 | 7.0 | 0 |
| hidden-middle | 300c obscure | 59.5% (52.5–70.8%) | 63.0% | 88 (1 of 3) | 147 | 17.7 | 0.3 |

Under other weights the picture holds: with Tier 2 = 1 and Tier 3 = 0.1,
attached runs stay at 0.4–3.6% and hidden-middle runs at 59–65%.

(Means over 3 runs. Per-run numbers: `summary.csv`; every run's details and
examples: `hallucination_scores.json`.)

- **With the whole file in view, nothing is invented.** All 9 attached runs
  returned all 300 rows; fixity error rates 0–8.4%. What it changed was the content
  of cells.
- **With the middle hidden, every run lost about half the sheet**, and 3 of
  6 runs on 300b/300c filled the gap with invented records: 144, 287 and
  264 rows. Checked against the Met's full catalogue, only 1 of these 687
  rows is a real Met record. 593 point to a real Met object page under a
  different title (`Lady in a Kimono`, `Esther Before Ahasuerus`,
  `Evangelist Mark`…), and 93 use links that don't exist. Every summary said
  the data was intact ("All substantive information remains intact").
- **Fame did not protect the records; it changed what went wrong.**
  - *Attached:* the known set had more altered rows than the obscure one (9.7
    vs 0.7 Tier 1 rows), because its famous Chinese and Japanese paintings have
    bilingual titles, and Haiku rewrote them: it deleted the Chinese and
    added English glosses, e.g. `元 王蒙 素庵圖 軸|Simple Retreat` →
    `Simple Retreat (by Wang Meng, Yuan Dynasty)`, and
    `五代 傳董元 溪岸圖 軸|Riverbank` → `Riverbank (Xuanhe Tu by Dong Yuan)`
    (溪岸圖 is *Riverbank*, not "Xuanhe Tu": an invented detail on one of the
    most famous paintings in the file). The random set's extra changes are
    mostly devised titles losing their square brackets and gaining "(Photograph)".
  - *Hidden middle:* the known set was never padded with invented rows (0 of
    3 runs; the model stopped at the rows it had seen), while random and
    obscure sets were (3 of 6). With 3 runs per cell this is suggestive, not
    established.
- **Dropped qualifiers are the commonest content change in typed copies:**
  `ca. 1928` → `1928`, `probably 1816` → `1816`, `dated 1767` → `1767`,
  `designed 1967–68; executed 1985` → `1985`.

## Caveats

- 3 runs per inventory and setup; the hidden-middle setup is engineered (see
  "Limitation to state up front" in NOTES.md).
- The score's rules encode judgement calls (what counts as reformat only);
  they were tuned on one hand-reviewed run, then on this spike's outputs
  while reading them, so a few edge cases may still be misjudged.
- Matching is by link: a correct row whose link the model changed would count
  as invented plus missing. No such case was seen.
- 300a's well-known works lean to paintings and include many East Asian
  scrolls with bilingual titles, so "known" is confounded with "has a
  non-English title" in the attached results.

## Files

- `config_attached.json`, `config_hidden_middle.json`, `cost_ledger.json`
  (both setups), `run_log_*.txt`.
- `changes.csv`: every difference found, uncompressed (reweigh with `scripts/fixity_rate.py`).
- `hallucination_scores.json` (per run, with examples), `summary.csv`.
- `runs/<id>/`: requests, responses, `output_files/` (hidden-middle), `response.md`, `meta.json`.
