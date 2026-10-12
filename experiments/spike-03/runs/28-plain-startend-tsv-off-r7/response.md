I can add the two columns, but the spreadsheet has no structured start/end year data. The only date information is the free-text "Object Date" field, which contains a wide variety of formats: single years ("1770"), approximate dates ("ca. 600–550 BCE"), century references ("18th century"), date ranges ("1830–40"), BCE dates, and some blank entries.

Here's how I'd fill the new columns:

- **Single year** → Start Year and End Year are both that year (e.g., "1770" → 1770 / 1770)
- **Range** → split into start and end (e.g., "1830–40" → 1830 / 1840; "1880–92" → 1880 / 1892)
- **"ca." dates** → I'd use the year with the "ca." prefix removed, or the range if given (e.g., "ca. 1896" → 1896 / 1896)
- **Century references** → the century's bounds (e.g., "18th century" → 1700 / 1799; "mid-19th century" → roughly 1840 / 1860; "late 16th–early 17th century" → 1575 / 1625)
- **BCE dates** → negative numbers or a "BCE" suffix, since they can't be compared with CE years as plain numbers
- **Blank or unknown** → left empty

Several entries, such as "Object ?", "Piece", "unknown", and rows with no date at all, will have to stay blank.

Could you tell me which format you'd like? Options include plain signed integers (BCE as negative, e.g., -600), or text with the era kept (e.g., "600 BCE"). Once you confirm, I'll produce the full table with the new columns. If you'd prefer, I can also output it as CSV or tab-separated text so you can paste it straight into a spreadsheet.