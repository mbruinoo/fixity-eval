# Review results (2026-10-17)

Answers as saved from the review page (`responses/`, one JSON per item).
Codes in backticks are in [GLOSSARY.md](../../GLOSSARY.md).

## 1. Convention review (`83995a`): 31 of 31 agreed

Every presumed rule held for every sampled object (6 photographs and 3 other
wholly bracketed titles, 6 `original|English` titles, 4 "(?)" dates, 3
"probably/possibly", 4 date qualifiers, 2 "ca.", 3 blank titles). The
reviewer's notes:

- `[Palm Trees, Florida]` (Walker Evans): the Met's notes say the photograph
  was found in an envelope labelled "July 1937"; the brackets very likely mark
  a title given by someone other than Evans.
- `[Acropolis, Athens, Greece]`: likely devised by the cataloguer.
- "1826 (reprinted posthumously)": must be kept. Standardizing may move the
  memo to a separate column, as long as it isn't dropped.

The rules in `spec/met_inventory_significant_properties.md` (`f9951b`) are
now recorded as reviewed (v1.1); the Met's own confirmation is still welcome.

## 2. Blind labelling of claims (`745dd8`): 30 of 100 labelled

The reviewer stopped at 30, judging them representative.

- **Precision**: all 30 sentences were judged integrity claims.
- **Truth**: 29 judged true or false (1 unsure). The scorer agreed on
  **25 of 29** (86%), meeting the 85% bar set in the pre-registration draft.
- **All 4 disagreements** were counts one higher than the rows ("all 101
  records" for a 100-row file; "301 entries" for 300), which the scorer had
  accepted as "counting the header". The reviewer judged them false: a
  record count that includes the header is wrong. One of them was a
  "preserved" sentence whose count was wrong, which the reviewer judged false
  as a whole.
- **Revision** (made after seeing these labels, so it is a calibration, not
  a blind result): a count of rows + 1 is true only if the sentence says the
  header is included, and a sentence is false if any checkable part of it is
  false. Agreement after revision: 29 of 29. Header-only miscounts are kept as
  their own kind (`row_count_plus_header`), so the corpus report shows
  theatre with and without them.
- Not measured: recall (claims the finder missed), and the 70 unlabelled
  items.

## 3. Changes, graded with the reviewer's scale (`db71ca`)

The reviewer set the severity scale (in the spec, `f9951b`) and asked Claude
to grade the 45 changes with it: `3_losses_graded_by_claude.csv`, with a
reason for each. **These are Claude's grades, not an independent human
review**; a spot-check of some of them by the reviewer would measure
agreement.

The sheet's first version included 8 cases where a dropped closing quote had
merged several following rows into one cell; they were excluded (they're
counted as missing rows elsewhere), and each card now shows a word-level
diff.

| Grade | Changes | Typical cases |
|---|---|---|
| no change of meaning | 1 | "1782, 2nd edition" → "1782 (2nd edition)" |
| 1 Minor | 14 | placeholders for blank titles (5); original-language title moved after the English, bar removed, all text kept (4); a redundant gloss or qualifier removed |
| 2 Moderate | 29 | "(?)" removed (5); devised-title brackets removed (4); original-language title removed, often with the artist's name (5); issuer, source or edition removed; titles cut short |
| 3 Severe | 1 | "19th–20th century [bell dated ca. 1480]" → "1673", another object's date |

By the scorer's tag: every "original script removed" and "uncertainty
removed" was Moderate; every placeholder was Minor; "other rewrite" was
mostly the moved-but-kept original-language titles (Minor). The tags are
rough: the one Severe change was tagged "brackets removed" (its "[bell dated
…]" note disappeared, along with the whole date), and "quotes changed" held
real losses as well as formatting. 44 of the 45 changes the scorer flagged
change meaning on the reviewer's scale.
