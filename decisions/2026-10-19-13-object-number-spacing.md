# 13. Spacing and separators in object numbers

- **Date:** 2026-10-19
- **Status:** approved by the repo author in chat, 2026-10-18 and 2026-10-19.
  Settles what record 02 left open. Also records the author's confirmation
  (2026-10-18) of record 12's second bullet: one "no date" wording may
  replace another, in dates only.

## Context

Record 02 left the spacing and separators in object numbers open, weighted 0
for the time being. Object numbers are identifiers: a space or a mark can
separate parts of a number (`45.24.10, .30a, b` is three objects or parts),
so a change that looks small can make a different number.

## Decision

| Change in an object number | Example | Weight |
|---|---|---|
| Dash style (record 02, a) | `2002.201.82a–p` → `2002.201.82a-p` | 0 |
| Spacing that separates nothing differently | a double space made single; a space after a comma added or removed; `#49 p62` → `#49p62` (the letter still separates the parts) | 0 |
| A space removed or added next to a decimal point | `#49 .620` → `#49.620` (could now read as one value, 49.620) | 0.25 per character (minor) |
| A space removed or added between two digits | `#49 62` → `#4962` (a different number) | 1.0 per character |
| A separator mark changed, added, removed or moved | `45.24.10, .30a, b` → `45.24.10; .30a; b` (either the marks mean something or they don't; a different mark could signal a different grouping) | 0.25 per character (minor) |
| Anything else (a digit or letter changed, added or removed) | `45.24.10` → `45.24.11` | 1.0 per character |

## Consequences

- `scripts/hallu_score.py` grades object numbers with these rules
  (`object_number_change`); `tests/` covers each example.
- A change of letter case in an object number (`14.40.872A` for
  `14.40.872a`) falls under "anything else", at full weight: unlike a title,
  an identifier's letters are part of it. The exploratory scorer counted it as
  a slight loss by accident. Raised with the repo author.
- Spec v1.1's rule that an object number must survive as an exact string
  now has these exceptions; `spec/met_inventory_significant_properties.md`
  gets a version bump (v1.3) with a dated note.
