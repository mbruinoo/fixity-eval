I can add those columns, but the spreadsheet data is needed in a usable form. The "Object Date" column contains free-text dates in many formats (e.g., "17th century", "ca. 1427–1400 B.C.", "January 1st, 1874", "late 19th to early 20th century", "first half of the 5th century BCE", blank cells), and parsing those into numeric start and end years requires interpreting each entry.

Here is the approach I'd take, with the result for each row:

- **Single years** ("1857", "1983"): Start Year = End Year = that year.
- **Ranges** ("1760–70", "1960–79", "1723–26"): Start and End from the range (with the two-digit end completed, e.g., 1760–70 → 1760, 1770).
- **Centuries** ("17th century"): Start = 1600, End = 1699.
- **Partial centuries** ("first half of the 5th century BCE", "second quarter of the 5th century BCE"): Start and End from the subdivision (e.g., first half of 5th c. BCE → 500 BCE to 450 BCE).
- **Decades** ("1930s", "1960–79"): Start = first year, End = last year of the decade.
- **Circa / approximate dates** ("ca. 1740–94"): Use the numbers given, ignoring "ca."
- **"or" dates** ("1901 or 1902"): Start = 1901, End = 1902.
- **Full dates** ("August 17, 1864"): Start = End = 1864.
- **Blank dates**: Leave both columns blank.
- **Unknown-century dates** ("probably 4th century BCE"): Use the century range.

Because there are roughly 400 rows, I'd recommend one of two options:

1. **Paste the output as CSV** and I'll return the full table with the two new columns. I'd note that BCE dates would be shown as negative numbers (e.g., −500) so they sort correctly, unless you prefer a different convention.
2. **Use a formula in your spreadsheet** if you want it to stay live, though free-text dates like these are hard to parse with formulas alone.

Shall I proceed with option 1? If you want the full table returned, let me know, and also whether you'd like BCE years as negative numbers or as text like "500 BCE."