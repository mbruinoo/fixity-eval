# Manual run in claude.ai: Haiku 5.5, effort medium

Run by the researcher on 2026-10-13 in claude.ai (incognito), Haiku 5.5 at
medium effort. Uploaded `data/met_random_300.tsv` (renamed
`met_inventory_261013.tsv`) and sent `Can you standardize this .tsv file?`.
The model thought for 11 seconds and returned the sheet in a code block.

`claude_ai_haiku55_medium_output.tsv` is that code block, saved from the
pasted chat transcript. Copying may have turned ideographic spaces (U+3000)
into ordinary spaces, so changes of that kind are uncertain.

## Result

Checked with `python scripts/compare_tsv.py data/met_random_300.tsv experiments/spike-04/manual/claude_ai_haiku55_medium_output.tsv`
and a cell-by-cell diff.

- **No made-up content.** All 300 rows, same order, same object numbers; no
  invented rows or values.
- **29 changed cells match its summary:** all 300 links `http` → `https`,
  `B.C.` → `BCE` and range spacing in dates, curly quotes straightened, HTML
  entities removed, a trailing period dropped.
- **4 changes it didn't mention, one contradicting its summary**
  ("Untouched: … non-English titles"):
  - `东周 玉璜` → `東周 玉璜` (a simplified character swapped for the traditional form)
  - `蝉小川|The Cicada Stream (Semi no Ogawa)  蝉小川` → trailing `蝉小川` deleted
  - `dallÁrchitetto` → `dall'Architetto` (a source error silently corrected)
  - `dated A.H. 37?/ 98 CE ?` → `dated A.H. 37?/98 CE?` (spacing)
- Possibly also: ideographic spaces in 4 Chinese/Japanese titles turned into
  ordinary spaces (may be a copying artifact).
