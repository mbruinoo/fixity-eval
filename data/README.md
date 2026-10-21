# Data

Three inventories from the Metropolitan Museum of Art Open Access dataset
([`MetObjects.csv`](https://github.com/metmuseum/openaccess/blob/master/MetObjects.csv),
CC0), each with four columns: Object Date, Title, Object Number, Link Resource.
Tab-separated, UTF-8, no quoting. Copied unchanged from
`exploratory@0277caf`, where the other data files of the exploratory phase
remain (`git show 0277caf:data/README.md`).

The source file used for all three: `MetObjects.csv`, 484,956 rows,
downloaded 2026-10-12, SHA-256
`de617b9c947458e426111207f81a65bd1379a151c0077d3ce29cfc22fc0b9183`. The Met
updates it from time to time, so a fresh download may give different samples.

| File | Rows | Use | SHA-256 |
|---|---|---|---|
| `met_inventory_f.tsv` | 100 | **Held out**: confirmatory runs only; frozen | `a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf` |
| `met_inventory_e.tsv` | 100 | Tuning, pilots and tests; never confirmatory | `e12ad41337e53ce8bea32d72c0ce8459a2559d069e89390c7df75bf51edab3bf` |
| `met_inventory_300b.tsv` | 300 | Tuning, pilots and tests; never confirmatory | `33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547` |

See `decisions/2026-10-18-04-held-out-file.md`.

## `met_inventory_f.tsv` (held out)

100 Met objects drawn by `scripts/make_heldout_sample.py` (seed 11),
stratified so each cataloguing convention in
`spec/met_inventory_significant_properties.md` is well represented: 12
wholly bracketed (devised) titles, 12 with non-Latin script, 10 dates with a
question mark, 8 with "probably"/"possibly", 10 with a parenthetical date
qualifier, 10 blank titles, 8 with quotation marks in the title, 8 ranges or
lists of object numbers, and 22 with none of these; sorted by title. No
object in it appears in any earlier inventory file. Never given to a
session during the exploratory phase. Two of its objects appear in
`exploratory:data/fame_sample_round2.csv`, the list used in spike-05's
memory probe (asking Haiku 4.5 what it knew about an object). Which rows
carry each convention is listed in `spec/canaries.json`.

The script refuses to overwrite the file. `--stats` only counts conventions
in the source.

## `met_inventory_e.tsv`

A "messy" 100-row inventory: a larger share of what typing out tends to damage
(long titles, non-Latin and bilingual titles, uncertain dates, ID ranges, blank
titles), as in many real archival inventories. Drawn from `MetObjects.csv` by
`scripts/make_messy_sample.py` (seed 7; strata: 33 long titles, 17 non-Latin,
10 uncertain dates, 10 ID ranges, 8 blank titles, 22 random), skipping objects
already in the 300-row inventories, sorted by title. As drawn: 36 titles over
100 characters, 17 non-Latin, 25 uncertain dates (incl. "ca."), 15 ID ranges, 8
blank titles; about 14,600 characters. Used to tune wordings in spikes 25–32.

```
python scripts/make_messy_sample.py MetObjects.csv data/met_inventory_e.tsv
```

## `met_inventory_300b.tsv`

300 randomly sampled Met rows (the first 300 rows of the exploratory phase's
1,000-row sample, drawn stratified by department, seed 43), sorted by title,
25 of them with blank titles. The base case of the exploratory phase was set
on this file (a viewer that hides the middle of the file). Its generating
steps are in `exploratory@0277caf:data/README.md`.
