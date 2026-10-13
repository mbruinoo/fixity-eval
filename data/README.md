# Data

## `met_sample_200.csv`

200 rows sampled from the Metropolitan Museum of Art Open Access dataset
([`MetObjects.csv`](https://github.com/metmuseum/openaccess/blob/master/MetObjects.csv), CC0).

- **Method:** stratified by `Department` with proportional allocation (largest
  remainder), random within each department, rows shuffled. Seed `42`.
  See `scripts/sample_met.py`.
- **Columns:** all 54 original columns, values unchanged. Rows with an empty
  `Object Date` are kept (9 of 200, about the same as the ~2.8% in the full set).
- **Source file:** 484,956 rows, downloaded 2026-10-12,
  SHA-256 `de617b9c947458e426111207f81a65bd1379a151c0077d3ce29cfc22fc0b9183`
- **Sample file:** SHA-256 `0c91e70c4e9bff3143ee2db961ec42ec2595db26c74463bd06bc6f370577fdf4`

To regenerate:

```
curl -L -o MetObjects.csv https://media.githubusercontent.com/media/metmuseum/openaccess/master/MetObjects.csv
python scripts/sample_met.py MetObjects.csv data/met_sample_200.csv
```

The Met updates the upstream file from time to time. If the source checksum
doesn't match the one above, you'll get a different sample.

## `met_sample_200_trimmed.csv`

The same 200 rows, in the same order, with just five columns: `Object Date`,
`Title`, `Artist Display Name`, `Object Number`, `Link Resource`. Values are
copied exactly. Some cells are empty in the source and stay empty here:
75 `Artist Display Name`, 9 `Object Date`, 8 `Title`.

- **Sample file:** SHA-256 `09724414bd42116e1399fa00a11cd948cb9905e66cc2d2f0cc681809b1d0c221`

To regenerate from the full sample:

```
python scripts/trim_sample.py data/met_sample_200.csv data/met_sample_200_trimmed.csv
```

## `met_sample_1000.csv`, `met_sample_1000_trimmed.csv`, `met_sample_500_trimmed.csv`, `met_sample_50_trimmed.csv`

- **1000:** a separate draw, same method, seed `43` (all 54 columns), and its
  five-column trim. SHA-256 `5aaa5979…7f43` (full) and `195c8e74…0ee9` (trimmed).
- **500:** the first 500 rows of the 1,000-row trim.
- **50:** the first 50 rows of `met_sample_200_trimmed.csv`.
- **`met_sample_200_trimmed.tsv`:** the 200-row trim as TSV (fields joined by
  tabs, no quoting; no value contains a tab or line break). SHA-256 `ca42753f…6656`.

```
python scripts/sample_met.py MetObjects.csv data/met_sample_1000.csv --n 1000 --seed 43
python scripts/trim_sample.py data/met_sample_1000.csv data/met_sample_1000_trimmed.csv
head -501 data/met_sample_1000_trimmed.csv > data/met_sample_500_trimmed.csv
head -51 data/met_sample_200_trimmed.csv > data/met_sample_50_trimmed.csv
```

## 100-row variants (`met_sample_100_*`)

All are the first 100 rows of `met_sample_200_trimmed.csv`.

- `met_sample_100_trimmed.csv`: all five columns.
- `_nourl.csv`: without Link Resource. `_date_title_artist.csv`: only those three.
  `_nodate.csv`: without Object Date. `_title_artist.csv`: only those two.
- `_blanked35.csv` / `.tsv`: 35 dated rows (chosen with `random.Random(7)`)
  have their Object Date emptied, so 39 of 100 are blank. The blanked row
  numbers are in `_blanked35_rows.json`; the real dates are in `met_sample_200.csv`.

## `met_t206_300.tsv`, `met_random_300.tsv`

Real Met rows as TSV (Object Date, Title, Object Number, Link Resource),
sorted by title. T206: 300 of the 538 rows whose title contains `(T206)`,
`DataFrame.sample(300, random_state=42)` from `MetObjects.csv` (SHA-256
`a3df42a2…d181`). Random: the first 300 rows of `met_sample_1000_trimmed.csv`
(SHA-256 `33c53888…d547`).

## `met_random_1000.tsv`

`met_sample_1000_trimmed.csv` as TSV (Object Date, Title, Object Number, Link
Resource), sorted by title. One row whose title contains a line break is left
out, so it has 999 data rows. 118,372 bytes. Made for trying the spike-04
setup in a chat app, where a longer file is more likely to be read only in part.

## `fame_sample.csv`

1,433 Met objects for the spike-05 recall probe (`scripts/fame_probe.py sample`),
with the Met's own artist, dates, medium and highlight flags: the 277 titled
objects of `met_random_300.tsv`, 8 famous anchors, 348 Met highlights, 400
random non-highlights with a named artist, and 400 random non-highlights.

## `met_inventory_300a.tsv`, `met_inventory_300b.tsv`, `met_inventory_300c.tsv`

Three 300-row Met inventories with the same columns as `met_random_300.tsv`
(Object Date, Title, Object Number, Link Resource), sorted by title, for
comparing well-known and obscure works. Scores are Haiku 4.5's `known_score`
from spike-05; no object appears in more than one file.

| File | What it is | Blank titles |
|---|---|---|
| 300a | 275 of the best-known objects scored (artist and year both right; mean familiarity 0.57), plus 25 untitled Met highlights or timeline works | 25 |
| 300b | a copy of `met_random_300.tsv` (random; mean known_score 0.14, familiarity 0.16) | 25 |
| 300c | 275 random objects with known_score 0 and familiarity ≤ 0.1, plus 25 untitled random non-highlights | 25 |

- 300a comes from 3,933 scored objects (spike-05 round 1, plus round 2's
  2,500 Met highlights and timeline works with a named artist). It leans to
  paintings and design classics. Its 25 lowest-familiarity rows were swapped
  for the untitled ones.
- Untitled objects can't be scored, so each file's 25 untitled rows are chosen
  by group instead: Met highlights or timeline works for 300a (mostly
  anonymous Asian and Islamic objects), ordinary objects for 300c. All three
  files now have 25 untitled rows, so blanks don't differ between them.

SHA-256: 300a `7c1e1077…5751`, 300b `33c53888…d547`, 300c `f5eace76…40a1`.
