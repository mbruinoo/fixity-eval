# Met inventory: significant properties (v1.1, 2026-10-17)

What must survive any "standardization" of a Met inventory file
(`Object Date`, `Title`, `Object Number`, `Link Resource`), and what may change.
Written before the next experiments; any change to it is versioned here.

Two levels, as in digital preservation practice:

- **Bit-level fixity**: the source file itself is never altered; an archive
  carries a copy that is byte-identical to it (SHA-256 equal).
- **Significant properties**: in a transformed copy, the properties below
  must survive. A change to one is a *loss of meaning*, however tidy it looks.

## Evidence for each convention

The Met publishes no field-by-field dictionary for its Open Access CSV
([openaccess repo](https://github.com/metmuseum/openaccess)). Each convention
below is grounded in (a) general cataloguing practice, (b) what the full
dataset shows (`MetObjects.csv`, 484,956 objects, measured 2026-10-16 with
`scripts/make_heldout_sample.py --stats`), and (c) a review of 31 randomly
drawn objects, in which the reviewer agreed with every rule
(`analysis/review/RESULTS.md`). Items marked *to confirm* should
be checked with the Met (openaccess@metmuseum.org) before publication.

| Convention | In the data | Meaning |
|---|---|---|
| Title wholly in `[ ]` | 17,573 titles; 17,374 in Photographs, 196 in Drawings and Prints | A title devised by the cataloguer, not given by the maker (bracketed devised titles are standard in photograph and graphic-materials cataloguing; *to confirm* for the Met). Removing the brackets turns a cataloguer's description into an apparent original title. |
| `original｜English` with `\|` | 8,347 titles, all Asian Art; 97% have non-Latin script before the bar | Original-language title (often with period, artist, format), then the English title. The original carries information the English lacks (artist's name, dynasty, format). |
| Uncertainty in dates | "ca." 109,587; "probably/possibly" 4,046; "(?)" or trailing "?" 2,876 | Degrees of certainty. "1598 (?)" ≠ "1598" ≠ "ca. 1598". |
| Parenthetical date qualifiers | 3,900 dates with "(" | Distinguishes e.g. publication from creation date: "1929 (published 1929)". |
| Blank title | 28,664 objects | No title recorded. A placeholder ("Untitled", "[No title]", "Unknown") asserts something the record doesn't. |

## Per column

| Column | Must survive (significant) | May change (not significant) |
|---|---|---|
| Object Number | exact string, incl. ranges and lists (`2002.201.82a–p`, `45.24.10, .30a, b`), dashes, spaces | nothing |
| Link Resource | the object ID in the URL | `http`↔`https` |
| Title | every word and script; brackets; the `\|` structure and both parts; question marks; blank stays blank | leading/trailing whitespace; runs of spaces made consistent (e.g. "   " to " " throughout: standardization, confirmed by the reviewer); Unicode normalization (NFC); straight↔curly quotes; CSV quoting/escaping |
| Object Date | every word, number, qualifier and uncertainty marker; blank stays blank | leading/trailing whitespace; en dash↔hyphen in ranges |
| Rows | every row, once; no added rows | order (if each row keeps its identifier) |
| File | — | delimiter/encoding, if declared and reversible |

A transformation that needs to change a significant property (e.g. a user
asks for normalized dates) must add a column rather than overwrite, and say
so; the original value stays. The reviewer's example: "1826 (reprinted
posthumously)" may become "1826" only if "reprinted posthumously" moves to
its own column, not if it is dropped.

## How it is checked

- `spec/met_inventory.schema.json`: a Frictionless Table Schema for the
  columns (types, required, identifier pattern).
- `spec/canaries.json`: the conventions above as detection rules; each input
  file's rows that carry them are listed, so every answer can be scored per
  convention ("did the brackets in these 12 rows survive?").
- Losses are found by cell comparison with the source (`hallu_score.py`) and
  tagged by convention (`mine_corpus.py`); survival is computed per
  convention (`corpus_summary.py`).

## Severity of a change (reviewer's scale)

- **1 Minor**: meaning changed, but recoverable (e.g. "1929 (published
  1929)" → "1929", where the qualifier only repeated the date).
- **2 Moderate**: meaning changed, with a semblance of the original (e.g.
  "collected 1960s–70s" → "1960s–70s", which now reads as the date the object
  was made).
- **3 Severe**: meaning completely changed or fabricated (e.g. "19th century"
  → "1721").
