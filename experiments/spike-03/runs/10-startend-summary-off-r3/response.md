I can't reliably produce the full updated CSV by hand for this many rows (about 240), and doing so would risk silent errors in the data, so I won't present it as complete. Instead, here is the approach that will get you a correct result without running code:

**Option 1: Spreadsheet formulas (no code)**
Paste the CSV into Excel or Google Sheets, then add two columns to the right of "Link Resource" with these formulas in row 2 and fill down:

- Start Year: `=IFERROR(VALUE(REGEXREPLACE(A2,"^.*?(\d{3,4}).*$","$1")),"")`

This pulls the first 3–4 digit number from the date, which handles "1770", "ca. 1896", and "1830–40". For centuries ("18th century", "6th–7th century"), it will return the wrong value, so those rows need manual handling.

- End Year: a parallel formula that pulls the second number when a range is present, otherwise repeats the start year.

**Option 2: Manual conversion rules you can apply**
- Single year ("1770", "ca. 1896") → Start = End = that year
- Range ("1830–40", "1850–1914") → Start = first year, End = second (expand "40" to "1840")
- Century ("18th century") → Start 1700, End 1799; "late 18th century" → 1750, 1799; "early 20th century" → 1900, 1930
- BCE dates → negative years (e.g., 530 BCE → -530)
- Unknown/blank dates → leave both empty

**Count of unconvertible dates:** Many rows are blank, "unknown", "n.d.", or "Object ?"-style entries. Expect roughly 15–20 rows that will end up blank.

If you'd like, paste a smaller batch (say 20–30 rows) and I'll return the converted CSV for that batch, with an exact count of rows processed, dates left blank, and confirmation that all other columns are unchanged. Batching this way lets me check every row reliably.