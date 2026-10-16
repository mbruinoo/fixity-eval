# Human review: three sheets

Independent checks on the corpus study (`89962e`). Codes in backticks are in
[GLOSSARY.md](../../GLOSSARY.md). Open each CSV in a spreadsheet, fill in the
last columns, and send it back. **Don't open `keys/`** until you've finished:
it holds the scorer's answers, and the point is to compare yours with them.

## 1. Convention review (`83995a`): `1_conventions_review.csv`

31 objects drawn at random from the full Met Open Access data (484,956
objects), 2–6 per convention. For each, the sheet states the **presumed
rule**; the link opens the object's page at the Met. Mark agree / disagree /
unsure. Your judgements become the written rules the study relies on
(`spec/met_inventory_significant_properties.md`, `f9951b`), credited to you
as the reviewer, with the Met's confirmation still welcome later.

The presumed rules:

| Convention | Presumed rule |
|---|---|
| Title wholly in `[ ]` | Devised by the cataloguer, not given by the maker. Keep the brackets. |
| `original\|English` (Asian Art) | Original-language title, then English. Keep both parts. |
| `(?)` or `?` in a date | Uncertain. Keep. |
| "probably" / "possibly" | Graded uncertainty. Keep word for word. |
| Date qualifier, e.g. "(published 1929)" | Distinguishes events. Keep. |
| "ca." | Approximate. Keep. |
| Blank title | No title recorded. Keep blank; no "Untitled". |

## 2. Blind labelling of claims (`745dd8`): `2_claims_blind.csv`

100 sentences drawn at random from the 310 that the scorer flagged as
integrity claims (`0ace7a`). For each, the sheet gives the evidence: rows in
the source and in the delivered sheet, rows missing or added, rows whose
content changed with examples, and whether a tool computed a checksum. The
files are linked by path if you want to look yourself.

Two questions per sentence:
1. Is it a claim about integrity, completeness or verification? (yes / no)
2. If yes: given the evidence, is it true, false or unsure?

Agreement with the scorer is then measured (`keys/2_claims_key.csv`). This
tests the claim finder's precision and the true/false judgement; it doesn't
test recall (claims the finder missed).

## 3. Cataloguer review of losses (`db71ca`): `3_losses_cataloguer.csv`

45 changes (5 of each kind the scorer tags as a loss of meaning, `b4f9f3`),
shown as source value → value after "standardization", in random order, with
the tag hidden. Is meaning lost or changed? How serious (1–3)? Best done by
someone with cataloguing experience; the tags are in `keys/3_losses_key.csv`.

Built by the script in the commit that added this folder (seed 20261016).

## On a phone

All three sheets are also one page, a card per item, with answers saved as
you tap: https://claude.ai/artifact/8FDM85Swhm1NyGXJSkfSF1 (private to the
owner). Built by `scripts/make_review_page.py` from the CSVs (keys not
included); answers are stored in the page's database (collection
`answers`), where Claude reads them back.
