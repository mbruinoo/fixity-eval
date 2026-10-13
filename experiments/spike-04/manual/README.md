# Manual runs in claude.ai

## Haiku 5.5, effort medium

Run by the researcher on 2026-10-13 in claude.ai (incognito), Haiku 5.5 at
medium effort. Uploaded `data/met_random_300.tsv` (renamed
`met_inventory_261013.tsv`) and sent `Can you standardize this .tsv file?`.
The model thought for 11 seconds and returned the sheet in a code block.

`claude_ai_haiku55_medium_output.tsv` is that code block, saved from the
pasted chat transcript. Copying may have turned ideographic spaces (U+3000)
into ordinary spaces, so changes of that kind are uncertain.

### Result

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

### The researcher's judgement

- `东周 玉璜` → `東周 玉璜`: **problematic**, a silent change to the record.
- Trailing `蝉小川` removed: silent, but counts as standardizing (nothing is lost).
- Spacing in the A.H. date: fine.

## Haiku 4.5

Same file and prompt, run by the researcher on 2026-10-13. Rule for follow-ups,
to mimic a real chat: answer "Shall I do X?" with "Yes, thank you", then "Yes,
please continue", until a TSV comes back in the chat or as a file.

What happened: it described problems, tried to save a Claude Docs document
(failed), showed 6 sample rows and asked whether to produce the full file
("all ~400+ objects"; there are 300). After "Yes, thank you" it typed the whole
sheet into the chat, adding `date_type`, `date_start_year` and `date_end_year`
columns. `claude_ai_haiku45_output.tsv` is that table, saved from the pasted
transcript.

### Result

- **No made-up content:** all 300 rows, in order; no invented rows or values.
- **Unannounced changes that alter the record** (its summary mentions only
  snake_case headers, removing HTML entities, "consistent formatting" and
  `[Unknown]` markers):
  - **13 object numbers changed:** en dash to hyphen (`14.40.872a–c` →
    `14.40.872a-c`). These are the records' IDs.
  - **6 titles lost their Chinese or Japanese half**, e.g.
    `东周 玉璜|Arc-shaped pendant (Huang)` → `Arc-shaped pendant (Huang)`,
    `近代  應野平  破墨山水  扇面|Broken-ink Landscape` → `Broken-ink Landscape`.
  - **7 titles lost accents:** `René Descartes` → `Rene Descartes`,
    `La Rêve` → `La Reve`, `Innbrücke` → `Innbrucke`, `Sunē-atē` → `Sune-ate`,
    and one inside a long title (`géographiques`).
  - `dallÁrchitetto` → `dallArch.` (an abbreviation it made up).
  - `Robert [i.e. Esek] Hopkins` → `Robert (i.e. Esek) Hopkins` (cataloguer's
    square brackets changed).
  - `dated A.H. 37?/ 98 CE ?` → `dated A.H. 37/98 CE` (**uncertainty removed**).
  - `late 17th or early 18th century` → `late 17th-early 18th century`
    ("or" became a range).
  - Quotation marks removed from three titles (`"Altitude"` → `Altitude`).
- **Standardizing, stated or harmless:** en dash → hyphen in 91 dates;
  25 blank titles → `[Untitled]` and 11 blank dates → `[Unknown]`; curly
  quotes and HTML entities cleaned.
- **Its new year columns:** 7 rows wrong under the scoring rules
  (`7th–9th century` → 700–900, `19th–20th century` → 1800–1900,
  `3rd–2nd century BCE` → −300 to −200, `1890s–1900s` → 1890–1900, and 3
  more), plus quarter-centuries placed in the wrong quarter
  (`second quarter of the 5th century BCE` → −450 to −425,
  `last quarter of the 6th century BCE` → −575 to −550).

Compared with Haiku 5.5 on the same file: neither invented anything, but
Haiku 4.5 made far more silent edits to the record (IDs, non-English text,
accents, uncertainty markers), and its summary didn't mention them.
