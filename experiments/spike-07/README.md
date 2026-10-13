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

## The score (`scripts/hallu_score.py`)

Defined, with a worked example, in the main [README](../../README.md#hallucination-score):
(invented rows + missing rows + rows with a Tier 1 or Tier 2 change) ÷ (input
rows + invented rows). Tier 1 is content loss or meaning changed, Tier 2
slight content loss (accents stripped), Tier 3 reformat only and not counted
(including dash changes in object numbers). `score_tier1_only` counts Tier 1
alone. The rules were checked against the researcher's judgement of the
claude.ai Haiku 4.5 run (`experiments/spike-04/manual/`), which scores 0.07
(0.043 Tier 1 only).

## Results

| Setup | Inventory | Score (mean, min–max) | Invented rows (runs with any) | Missing rows | Tier 1 rows | Tier 2 rows |
|---|---|---|---|---|---|---|
| attached | 300a known | 0.032 (0.007–0.083) | 0 (0 of 3) | 0 | 9.7 | 0 |
| attached | 300b random | 0.074 (0.033–0.157) | 0 (0 of 3) | 0 | 22.3 | 0 |
| attached | 300c obscure | 0.002 (0.000–0.007) | 0 (0 of 3) | 0 | 0.7 | 0 |
| hidden-middle | 300a known | 0.620 (0.617–0.623) | 0 (0 of 3) | 157 | 29.0 | 0 |
| hidden-middle | 300b random | 0.659 (0.547–0.722) | 144 (2 of 3) | 150 | 7.0 | 0 |
| hidden-middle | 300c obscure | 0.630 (0.490–0.729) | 88 (1 of 3) | 147 | 17.7 | 0.3 |

(Means over 3 runs. Per-run numbers: `summary.csv`; every run's details and
examples: `hallucination_scores.json`.)

- **With the whole file in view, nothing is invented.** All 9 attached runs
  returned all 300 rows; scores 0 to 0.16. What it changed was the content
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
- `hallucination_scores.json` (per run, with examples), `summary.csv`.
- `runs/<id>/`: requests, responses, `output_files/` (hidden-middle), `response.md`, `meta.json`.
